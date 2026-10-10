#!/usr/bin/env python3
"""List what is wider than the A4 text width in print, the cause of a shrunk PDF (build/qa/pdf_scale.py).

    uv run python build/qa/print_width.py dist/preview/lm/lm04.html [more pages]   # exit 1 if anything sticks out

Lays each page out as build/render_pdf.py does (900 px, details open, print media, charts re-rendered), then at the
A4 text width (680 px), and reports the innermost elements whose right edge passes it. KaTeX's stretchy SVG paths are
skipped: their boxes are clipped and never print outside the formula.
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

JS = r"""() => {
  const W = document.documentElement.clientWidth, out = [];
  for (const e of document.querySelectorAll('main *')) {
    if (e.closest('svg') && e.closest('.katex')) continue;
    const r = e.getBoundingClientRect();
    if (r.width === 0 || r.right <= W + 1) continue;
    if ([...e.children].some(c => c.getBoundingClientRect().right > W + 1)) continue;
    const box = e.closest('.katex-display, .exhibit, .co, table, pre, figure, p, li') || e;
    out.push(Math.round(r.right) + ' px  ' + box.textContent.replace(/\s+/g, ' ').slice(0, 90));
  }
  return [...new Set(out)];
}"""


async def main():
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        for a in sys.argv[1:]:
            pg = await b.new_page(viewport={"width": 900, "height": 1200}, color_scheme="light")
            await pg.goto(Path(a).resolve().as_uri(), wait_until="networkidle")
            await pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
            await pg.evaluate("document.fonts.ready")
            await pg.emulate_media(media="print")
            await pg.wait_for_timeout(800)
            await pg.evaluate("window.Book && window.Book.renderCharts && window.Book.renderCharts()")
            await pg.set_viewport_size({"width": 680, "height": 1200})
            await pg.wait_for_timeout(600)
            items = await pg.evaluate(JS)
            print(f"{a}: {len(items) or 'nothing'} wider than 680 px" + "".join(f"\n   {x}" for x in items[:20]))
            bad += bool(items)
            await pg.close()
        await b.close()
    sys.exit(1 if bad else 0)

asyncio.run(main())
