import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright


def to_url(a): return a if "://" in a else Path(a).resolve().as_uri()   # accept a file path or a URL
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": int(sys.argv[2]), "height": 900})
        await pg.goto(to_url(sys.argv[1]), wait_until="networkidle"); await pg.wait_for_timeout(500)
        res = await pg.evaluate("""() => { const W = document.documentElement.clientWidth; const out = [];
          for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect();
            if (r.right > W + 1 && r.width > 0) { let p = el.parentElement, clipped = false;
              while (p) { const cs = getComputedStyle(p); if (cs.overflowX === 'auto' || cs.overflowX === 'hidden' || cs.overflowX === 'scroll') { clipped = true; break; } p = p.parentElement; }
              if (!clipped) out.push(el.tagName + '.' + (el.className && el.className.baseVal === undefined ? el.className : '') + ' #' + el.id + ' right=' + Math.round(r.right) + ' w=' + Math.round(r.width)); } }
          return out.slice(0, 25); }""")
        print("\n".join(res)); await b.close()
asyncio.run(main())
