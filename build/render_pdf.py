import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright


def to_url(a): return a if "://" in a else Path(a).resolve().as_uri()   # accept a file path or a URL
SRC, OUT, TITLE = to_url(sys.argv[1]), sys.argv[2], sys.argv[3]   # page (path or URL), PDF path, footer title
FOOT = ('<div style="width:100%;font-family:Archivo,Arial,sans-serif;font-size:7.5pt;color:#69707a;padding:0 15mm;display:flex;justify-content:space-between">'
        f'<span>From Calculus to Kelly · {TITLE}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 900, "height": 1200}, color_scheme="light")
        await pg.goto(SRC, wait_until="networkidle")
        await pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
        await pg.evaluate("document.fonts.ready")
        await pg.emulate_media(media="print")
        await pg.wait_for_timeout(800)
        await pg.evaluate("window.Book && window.Book.renderCharts && window.Book.renderCharts()")
        await pg.wait_for_timeout(400)
        await pg.pdf(path=OUT, format="A4", print_background=True, display_header_footer=True,
                     header_template="<div></div>", footer_template=FOOT,
                     margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        await b.close()
asyncio.run(main())
