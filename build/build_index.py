"""Landing page: roadmap, contents, conventions, edition notes. Output is content-only (the artifact
publisher wraps the main page in its own document skeleton)."""
import html
import re

import build as B

ROOT = B.ROOT; SYL = B.SYL; AVAIL = B.AVAILABLE

def esc(s): return html.escape(s, quote=True)

# ---------------------------------------------------------------- roadmap diagram (hand-authored SVG)
def roadmap_svg():
    W, H, nw, nh = 720, 616, 214, 56
    col = {"L": 128, "M": 360, "R": 592}
    rowy = [28, 132, 236, 340, 444, 548]
    nodes = {  # id: (col, row, title, lms)
        "I": ("M", 0, "Calculus for Finance", "LM1–7"),
        "II": ("L", 1, "Linear Algebra for Portfolios", "LM8–12"),
        "III": ("R", 1, "Probability", "LM13–18"),
        "IV": ("M", 2, "Statistical Inference", "LM19–26"),
        "V": ("L", 3, "Portfolio Optimization", "LM27–31"),
        "VI": ("M", 3, "True Risk and Return", "LM32–35"),
        "VII": ("R", 3, "Stochastic Calculus", "LM36–40"),
        "VIII": ("M", 4, "Kelly and Optimal Leverage", "LM41–46"),
        "IX": ("M", 5, "Capstone", "LM47–50"),
    }
    def box(k):
        c, r, *_ = nodes[k]; x = col[c] - nw / 2; y = rowy[r]; return x, y
    def anchor(k, side):
        x, y = box(k)
        return {"top": (x + nw / 2, y), "bottom": (x + nw / 2, y + nh), "left": (x, y + nh / 2), "right": (x + nw, y + nh / 2)}[side]
    edges = [  # (from, to, label, route)
        ("I", "II", "gradients, Lagrange", "elbow"),
        ("I", "III", "integrals, series", "elbow"),
        ("III", "IV", "distributions", "elbow"),
        ("III", "VII", "random walks", "down"),
        ("II", "V", "wᵀΣw", "down"),
        ("IV", "V", "estimated μ, Σ", "elbow"),
        ("IV", "VI", "sampling error", "down"),
        ("VII", "VIII", "Itô, GBM", "elbow"),
        ("V", "VIII", "tangency portfolio", "elbow"),
        ("VI", "VIII", "uncertainty in μ", "down"),
        ("VIII", "IX", "sizing rules", "down"),
    ]
    out = [(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Prerequisite map: calculus feeds linear algebra and probability; '
            'probability feeds statistics and stochastic calculus; linear algebra and statistics feed portfolio optimization; '
            'statistics feeds risk measurement; portfolio optimization, risk measurement and stochastic calculus all feed the Kelly volume, which feeds the capstone." '
            'class="roadmap-svg">'),
           ('<defs><marker id="rm-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')]
    labels = []
    for a, b, lab, route in edges:
        ax, ay = anchor(a, "bottom"); bx, by = anchor(b, "top")
        if route == "down" and abs(ax - bx) < 1:
            pts = [(ax, ay), (bx, by - 2)]; lx, ly = ax + 8, (ay + by) / 2 + 4; anc = "start"
        elif a == "VII" and b == "VIII":
            pts = [(ax, ay), (ax, by + nh / 2), (anchor(b, "right")[0] + 2, by + nh / 2)]
            lx, ly = ax + 8, by + nh / 2 - 8; anc = "start"
        elif a == "V" and b == "VIII":
            pts = [(ax, ay), (ax, by + nh / 2), (anchor(b, "left")[0] - 2, by + nh / 2)]
            lx, ly = ax + 8, by + nh / 2 - 8; anc = "start"
        else:
            midy = (ay + by) / 2
            pts = [(ax, ay), (ax, midy), (bx, midy), (bx, by - 2)]
            lx, ly = (ax + bx) / 2, midy - 6; anc = "middle"
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        out.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="1.25" opacity="0.55" marker-end="url(#rm-arrow)"/>')
        labels.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{anc}" class="rm-edge">{esc(lab)}</text>')
    for k, (c, r, title, lms) in nodes.items():
        x, y = box(k)
        goal = k == "VIII"
        cls = "rm-node goal" if goal else "rm-node"
        out.append(f'<a href="#vol-{k}"><g class="{cls}"><rect x="{x:.0f}" y="{y:.0f}" width="{nw}" height="{nh}" rx="3"/>'
                   f'<text x="{x + 12:.0f}" y="{y + 21:.0f}" class="rm-k">VOL {k} · {lms}</text>'
                   f'<text x="{x + 12:.0f}" y="{y + 41:.0f}" class="rm-t">{esc(title)}</text></g></a>')
    out.extend(labels)
    out.append("</svg>")
    return "".join(out)

# ---------------------------------------------------------------- page
def build():
    ms = B.MathStore()
    M = lambda tex: ms.add(tex, False)
    total = sum(len(v["lms"]) for v in SYL["volumes"])
    # contents
    vols = []
    for v in SYL["volumes"]:
        rows = []
        for lm in v["lms"]:
            n = lm["n"]; ok = n in AVAIL
            title = f'<a href="lm/lm{n:02d}.html">{esc(lm["title"])}</a>' if ok else esc(lm["title"])
            if n in B.PUBLISHED:
                status = '<span class="st ok">Available</span>'
                if B.TARGET == "web" and not B.PREVIEW:
                    status += f'<br><a class="st-pdf" href="pdf/{B.pdf_name(n)}">PDF</a>'
            elif n in B.DRAFTS:
                status = '<span class="st rv">In review</span>'
            else:
                status = '<span class="st">Planned</span>'
            rows.append(f'<tr class="{"hl" if ok else ""}"><td class="n">LM{n}</td><td><div class="lm-t">{title}</div>'
                        f'<div class="lm-d">{B.md_inline(lm["desc"])}</div></td><td>{status}</td></tr>')
        vols.append(f'<section class="vol" id="vol-{v["id"]}"><h3><span class="vk">Volume {v["id"]}</span>{esc(v["title"])}</h3>'
                    f'<p class="vb">{esc(v["blurb"])}</p><div class="table-wrap"><table class="toc"><thead><tr><th>LM</th><th>Module</th>'
                    f'<th>Status</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>')
    # edition notes (newest first in syllabus.yaml) and the reading entry point
    editions = SYL.get("editions", [])
    ed_now = editions[0] if editions else {"version": "0.1"}
    edition_html = "".join(f'<p><strong>Edition {esc(str(e["version"]))} ({esc(str(e["date"]))}).</strong> {B.md_inline(e["notes"])}</p>'
                           for e in editions)
    if AVAIL:
        first = min(AVAIL); first_t = next(lm["title"] for v in SYL["volumes"] for lm in v["lms"] if lm["n"] == first)
        verb = "Read the sample module" if len(AVAIL) == 1 else "Start reading"
        start_link = f'<a class="start" href="lm/lm{first:02d}.html">{verb}: LM{first} {esc(first_t)} →</a>'
    else:
        start_link = ""
    guides = [p for p in B.PAGES if p["slug"] in B.AVAILABLE_PAGES]   # standalone pages; drafts show only in preview
    if guides:
        links = " · ".join(f'<a href="{p["slug"]}.html">{esc(p["title"])}</a>' + ("" if p["slug"] in B.PUBLISHED_PAGES else " (draft)")
                           for p in guides)
        start_link += f'<p class="cap new-here">New here? {links}</p>'
    goals = [
        ("Build statistical models", "Return distributions, regressions and factor models, GARCH volatility, cointegrated spreads — estimated, diagnosed and stated with their uncertainty.", "Vol III, IV"),
        ("Optimize portfolios under estimation error", "Mean–variance, risk parity and Kelly portfolios with realistic constraints, shrinkage estimators, and walk-forward evaluation.", "Vol II, V"),
        ("Measure true risk and return", "Geometric growth instead of arithmetic averages, confidence intervals for Sharpe ratios, Deflated Sharpe, costs and biases removed.", "Vol IV, VI"),
        ("Size positions with Kelly leverage", "From the binary bet to multi-asset leverage, with fat tails, parameter uncertainty, margin rules and drawdown limits.", "Vol VII, VIII"),
    ]
    goal_html = "".join(f'<div class="goal"><div class="gk">{esc(k)}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d, k in goals)
    legend = [
        ("definition", "Definition", "The precise statement of a term, in English."),
        ("example", "Example", "A worked problem with its full solution."),
        ("pitfall", "Pitfall", "A common mistake and how to avoid it."),
        ("zh", "導讀", "中文導讀：用中文把最難的直覺講清楚。"),
        ("deepdive", "Deep Dive", "Optional proofs and rigorous detail, collapsed by default."),
        ("kc", "Knowledge Check", "A short question with a hidden answer."),
        ("exhibit", "Exhibit", "Tables and charts, numbered within each module; charts show values on hover."),
        ("widget", "Interactive", "Sliders that let you move the parameters of a result."),
    ]
    legend_html = "".join(f'<div class="lg-item lg-{k}"><span class="lg-tag">{esc(t)}</span><span class="lg-d">{esc(d)}</span></div>' for k, t, d in legend)
    notation = [
        (M(r"R_t = \dfrac{P_t + D_t}{P_{t-1}} - 1"), "simple (holding-period) return; adds across assets"),
        (M(r"r_t = \ln(1+R_t)"), "log return; adds across time"),
        (M(r"\mu = \mathbb{E}[R],\ \ \sigma^2 = \operatorname{Var}(R)"), "mean and variance of simple returns"),
        (M(r"g = \mathbb{E}[\ln(1+R)]"), "log growth rate per period (per year once annualized); what compounding delivers"),
        (M(r"G = W_T / W_0"), "growth factor over a holding period"),
        (M(r"A"), "periods per year used to annualize, always with its sample (243.1 sessions a year in the book's 0050 sample)"),
        (M(r"f,\ f^*"), "exposure, position value divided by equity (above 1 it is leverage); its growth-maximizing (Kelly) value"),
        (M(r"\mathrm{SR} = (\mu - r_f)/\sigma"), "Sharpe ratio of a return, per day or annualized (say which)"),
        (M(r"\varphi,\ \Phi"), "standard normal density and distribution function"),
        (M(r"B_t"), "standard Brownian motion (W stays wealth)"),
        (M(r"\mathbf w,\ \hat\Sigma,\ \mathbf w^{\top}\hat\Sigma\mathbf w"), "from Volume II (LM7 already writes vectors this way): bold lower case is a column vector, here the weights; the hatted Sigma is the sample covariance matrix; the third expression is a portfolio's sample variance; the raised T means transpose"),
        (M(r"=,\ \approx,\ :="), "exact; approximate with the neglected order stated; defined as"),
    ]
    notation_html = "".join(f"<tr><td>{a}</td><td>{esc(b)}</td></tr>" for a, b in notation)
    rail = B.rail(0, "root")
    body = f"""<title>From Calculus to Kelly</title>
{B.THEME_HEAD}
{B.FONTS_LINK}
<link rel="stylesheet" href="assets/katex/katex.min.css">
<link rel="stylesheet" href="assets/book.css">
<style>
.hero {{ padding-block: 2.2rem 0.6rem; }}
.hero .kick {{ font-family: var(--f-head); font-size: 0.8rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--ink-2); }}
.hero h1 {{ font-size: clamp(2.3rem, 6.5vw, 3.9rem); font-weight: 800; font-stretch: 78%; line-height: 0.98; margin: 0.5rem 0 0.8rem; letter-spacing: -0.01em; }}
.hero .sub {{ font-size: 1.18rem; color: var(--ink-2); max-width: 40rem; margin: 0 0 0.6rem; }}
.hero .zh {{ font-size: 1rem; color: var(--ink-2); max-width: 40rem; line-height: 1.8; margin: 0 0 1rem; }}
.hero .facts {{ display: flex; flex-wrap: wrap; gap: 0.4rem 0.5rem; font-family: var(--f-head); font-size: 0.8rem; }}
.hero .start {{ display: inline-flex; align-items: center; gap: 0.5rem; margin-top: 1.1rem; font-family: var(--f-head); font-weight: 700;
  background: var(--bar); color: var(--bar-ink); text-decoration: none; padding: 0.55rem 0.9rem; border-radius: 3px; }}
.hero .start:hover {{ text-decoration: underline; }}
.page h2.sh {{ font-size: 1.32rem; font-weight: 760; font-stretch: 86%; text-transform: uppercase; letter-spacing: 0.015em; border-top: 3px solid var(--ink); padding-top: 0.55rem; margin: 3rem 0 1rem; }}
.goals {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px; background: var(--rule); border: 1px solid var(--rule); }}
.goal {{ background: var(--surface); padding: 0.9rem 1rem 0.6rem; min-width: 0; }}
.goal .gk {{ font-family: var(--f-head); font-size: 0.7rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); }}
.goal h3 {{ font-size: 1.04rem; margin: 0.3rem 0 0.35rem; }}
.goal p {{ font-size: 0.93rem; color: var(--ink-2); margin: 0 0 0.4rem; }}
.roadmap {{ margin: 1rem 0 0.4rem; overflow-x: auto; scrollbar-width: thin; }}
.roadmap-svg {{ display: block; width: 100%; min-width: 560px; height: auto; color: var(--ink); font-family: var(--f-head); }}
.rm-node rect {{ fill: var(--surface); stroke: var(--ink); stroke-width: 1.25; }}
.rm-node.goal rect {{ fill: var(--accent-soft); stroke: var(--accent); stroke-width: 2; }}
.rm-node .rm-k {{ fill: var(--muted); font-size: 10.5px; font-weight: 700; letter-spacing: 0.08em; }}
.rm-node .rm-t {{ fill: var(--ink); font-size: 13.5px; font-weight: 700; }}
.rm-node.goal .rm-k {{ fill: var(--accent); }}
a:hover .rm-node rect {{ stroke-width: 2.25; }}
a:focus-visible .rm-node rect {{ stroke: var(--focus); stroke-width: 3; }}
.rm-edge {{ fill: var(--ink-2); font-size: 11px; paint-order: stroke; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round; }}
.cap {{ font-family: var(--f-head); font-size: 0.82rem; color: var(--muted); margin: 0.4rem 0 0; }}
.cap.new-here {{ margin-top: 0.8rem; }}
.legend-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 0.5rem; margin: 1rem 0; }}
.lg-item {{ display: grid; gap: 0.2rem; padding: 0.55rem 0.8rem; border-left: 3px solid var(--rule); background: var(--surface); font-size: 0.9rem; min-width: 0; }}
.lg-tag {{ font-family: var(--f-head); font-size: 0.72rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }}
.lg-d {{ color: var(--ink-2); }}
.lg-definition {{ border-color: var(--accent); background: var(--accent-soft); }} .lg-definition .lg-tag {{ color: var(--accent); }}
.lg-example {{ border-color: var(--panel-head); background: var(--panel); }} .lg-example .lg-tag {{ color: var(--ink-2); }}
.lg-pitfall {{ border-color: var(--amber); background: var(--amber-soft); }} .lg-pitfall .lg-tag {{ color: var(--amber); }}
.lg-zh {{ border-color: var(--seal); background: var(--seal-soft); font-family: var(--f-zh); }} .lg-zh .lg-tag {{ color: var(--seal); font-family: var(--f-zh); letter-spacing: 0.2em; }}
.lg-deepdive {{ border-color: var(--ink-2); background: var(--panel); }} .lg-deepdive .lg-tag {{ color: var(--ink-2); }}
.lg-kc {{ border-color: var(--accent); }} .lg-kc .lg-tag {{ color: var(--accent); }}
.lg-exhibit {{ border-color: var(--ink); }} .lg-exhibit .lg-tag {{ color: var(--ink); }}
.lg-widget {{ border-color: var(--accent); }} .lg-widget .lg-tag {{ color: var(--accent); }}
.steps {{ counter-reset: st; list-style: none; padding: 0 !important; display: grid; gap: 0.35rem; }}
.steps li {{ counter-increment: st; display: grid; grid-template-columns: 2rem 1fr; gap: 0.3rem; margin: 0; }}
.steps li::before {{ content: counter(st); font-family: var(--f-head); font-weight: 800; background: var(--bar); color: var(--bar-ink); width: 1.5rem; height: 1.5rem; display: grid; place-items: center; font-size: 0.8rem; margin-top: 0.15rem; }}
.vol {{ margin: 2rem 0 0; scroll-margin-top: 4.5rem; }}
.vol h3 {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.2rem 0.7rem; font-size: 1.25rem; margin: 0 0 0.3rem; }}
.vol .vk {{ font-size: 0.75rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); font-weight: 800; }}
.vol .vb {{ color: var(--ink-2); margin: 0 0 0.5rem; font-size: 0.97rem; }}
table.toc td.n {{ font-family: var(--f-head); font-weight: 700; color: var(--muted); white-space: nowrap; width: 3.6rem; }}
table.toc .lm-t {{ font-weight: 650; }}
table.toc .lm-d {{ color: var(--ink-2); font-size: 0.86rem; margin-top: 0.1rem; }}
.st {{ font-family: var(--f-head); font-size: 0.74rem; font-weight: 700; color: var(--muted); white-space: nowrap; }}
.st.ok {{ color: var(--good); }}
.st.ok::before {{ content: "● "; }}
.st.rv {{ color: var(--amber); }}
.st.rv::before {{ content: "◐ "; }}
.st-pdf {{ font-family: var(--f-head); font-size: 0.74rem; font-weight: 700; }}
.notation td:first-child {{ white-space: nowrap; width: 15rem; }}
@media (max-width: 520px) {{ .notation td:first-child {{ white-space: normal; width: auto; }} .notation td:first-child .katex {{ white-space: nowrap; }} }}   /* a long row keeps a readable second column; a formula stays whole */
@media (max-width: 640px) {{ .goals {{ grid-template-columns: minmax(0, 1fr); }} }}
</style>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar"><a class="brand" href="index.html">From Calculus to Kelly<small>量化數理教科書</small></a>
<span class="crumb">Contents and roadmap</span><span class="spacer"></span>
{B.THEME_TOGGLE}<button class="rail-toggle" type="button" aria-controls="rail" aria-expanded="false">Contents</button></header>
<div class="layout">
<nav class="rail" id="rail" aria-label="Book contents">{rail}</nav>
<main class="page" id="main">
<header class="hero">
<div class="kick">A curriculum in {len(SYL["volumes"])} volumes</div>
<h1>From Calculus<br>to Kelly</h1>
<p class="sub">A quantitative curriculum that starts from first-year calculus, statistics and linear algebra, and ends with statistical models, optimized portfolios and growth-optimal leverage you can build and defend yourself.</p>
<p class="zh">從大一的微積分、統計學與線性代數開始，一路推進到自建統計模型、投資組合統計最佳化、計算真正的風險報酬，以及在估計誤差下求最適凱利槓桿。內文以英文為主，難懂之處附中文導讀。</p>
<div class="facts"><span class="chip"><b>Scope</b> {len(SYL["volumes"])} volumes · {total} learning modules</span>
<span class="chip"><b>Published</b> {len(B.PUBLISHED)} of {total}</span>
<span class="chip"><b>Data</b> Taiwan &amp; US markets</span>
<span class="chip"><b>Edition</b> {esc(str(ed_now["version"]))}</span>
<span class="chip"><b>License</b> MIT</span></div>
{start_link}
</header>

<h2 class="sh" id="goals">What you will be able to do</h2>
<div class="goals">{goal_html}</div>

<h2 class="sh" id="roadmap">Roadmap</h2>
<p>Each volume hands specific tools to the volumes after it. The arrows name what is handed over. Everything converges on Volume VIII, where Kelly leverage needs stochastic calculus for the growth rate, portfolio theory for the multi-asset case, and honest risk statistics for the inputs.</p>
<figure class="roadmap">{roadmap_svg()}<figcaption class="cap">Prerequisite map of the nine volumes. Select a volume to jump to its modules.</figcaption></figure>

<h2 class="sh" id="how">How each module works</h2>
<p>Every module follows the same architecture, built for self-study with code.</p>
<ol class="steps">
<li><span><strong>Learning Outcomes</strong> with mastery boxes you can tick; your ticks are remembered in this browser.</span></li>
<li><span><strong>Learning Module Overview</strong>: the main results in a few lines.</span></li>
<li><span><strong>Motivating Case</strong>: a real market situation the module resolves, with verified data.</span></li>
<li><span><strong>Numbered sections</strong>, each mapped to an outcome: intuition, definition, derivation, exhibit, worked example, pitfall.</span></li>
<li><span><strong>Knowledge Checks</strong> inside sections; <strong>Practice Problems</strong> and full <strong>Solutions</strong> at the end.</span></li>
<li><span><strong>Glossary</strong> (English–中文) and <strong>References</strong>; a companion <strong>Jupyter lab</strong> reproduces every number.</span></li>
</ol>
<div class="legend-grid">{legend_html}</div>

<h2 class="sh" id="notation">Notation and conventions</h2>
<p>The same symbols mean the same thing in every module. Every approximation is marked and comes with the order of what it neglects; derivations are given in full or the result is labelled as stated without proof, with a reference.</p>
<div class="table-wrap"><table class="notation"><tbody>{notation_html}</tbody></table></div>

<h2 class="sh" id="contents">Contents</h2>
<p class="cap">A module is published after an independent review recomputes its numbers and checks its mathematics; until then it is listed as in review.</p>
{"".join(vols)}

<h2 class="sh" id="labs">Labs, data and environment</h2>
<p>Each module ships with a Jupyter notebook that rebuilds its exhibits. Labs are Polars-first and use NumPy, SciPy and Matplotlib; later volumes add statsmodels, cvxpy and arch. Taiwan data come from FinMind and US data from FinMind's US price tables. FinMind's licence does not allow its raw data to be redistributed, so the repository lists every file the book uses with a checksum: download them once with your own FinMind token, and the labs then run offline. The Python environment is managed by uv and pinned in <code>uv.lock</code>.</p>
<div class="code"><div class="code-h"><span>Shell</span><button class="copy" type="button">Copy</button></div><pre class="hl"><code>git clone https://github.com/Benjamin-Teng/Quant-math-for-beginner.git
cd Quant-math-for-beginner
uv sync                                  # Python 3.13 environment, versions pinned by uv.lock
export FINMIND_TOKEN="your-token"
uv run python data/fetch_finmind.py      # download the raw data and check every file
uv run python data/make_lab_data.py      # build each lab's data/ folder
uv run --with jupyterlab jupyter lab labs/</code></pre></div>

<h2 class="sh" id="edition">Edition notes</h2>
{edition_html}
<p class="cap">A personal study project. Educational material only; nothing here is investment advice. Text and code are released under the MIT License. Market data: FinMind.</p>
</main>
<aside class="outline" aria-label="On this page"><h2>On this page</h2><ol>
<li><a href="#goals">What you will be able to do</a></li><li><a href="#roadmap">Roadmap</a></li><li><a href="#how">How each module works</a></li>
<li><a href="#notation">Notation and conventions</a></li><li><a href="#contents">Contents</a></li>
<li><a href="#labs">Labs, data and environment</a></li><li><a href="#edition">Edition notes</a></li></ol></aside>
</div>
<script src="assets/book.js"></script>
"""
    rendered = ms.render()
    def mrep(m):
        i = int(m.group(1)); return f'<span class="math-inline" role="math" aria-label="{esc(ms.items[i]["tex"])}">{rendered[i]}</span>'
    body = re.sub(r"MATHPH(\d+)[DI]X", mrep, body)
    if B.TARGET == "web":   # a full HTML document for any static host
        head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<meta name="description" content="A nine-volume quantitative curriculum from first-year calculus, statistics and '
                'linear algebra to statistical modeling, portfolio optimization and Kelly leverage.">\n'
                '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n')
        body = head + body.replace("<a class=\"skip\"", "</head>\n<body>\n<a class=\"skip\"", 1) + "</body>\n</html>\n"
    out = B.OUT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    print(f"built {out.relative_to(ROOT)}", f"{len(body):,} bytes")

if __name__ == "__main__":
    build()
