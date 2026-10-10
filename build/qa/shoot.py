import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright


def to_url(a): return a if "://" in a else Path(a).resolve().as_uri()   # accept a file path or a URL
OUTDIR = os.environ.get("QA_OUT", "qa_shots"); os.makedirs(OUTDIR, exist_ok=True)
URL = to_url(sys.argv[1]); tag = sys.argv[2]; scheme = sys.argv[3] if len(sys.argv) > 3 else "light"; width = int(sys.argv[4]) if len(sys.argv) > 4 else 1400
sels = sys.argv[5].split("|") if len(sys.argv) > 5 else []
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": width, "height": 1000},
                              color_scheme="dark" if scheme == "dark" else "light", device_scale_factor=1)
        msgs = []
        pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text}"))
        pg.on("pageerror", lambda e: msgs.append(f"PAGEERROR: {e}"))
        await pg.goto(URL, wait_until="networkidle")
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=f"{OUTDIR}/{tag}-top.png")
        for i, s in enumerate(sels):
            el = pg.locator(s).first
            await el.scroll_into_view_if_needed()
            await pg.wait_for_timeout(200)
            await el.screenshot(path=f"{OUTDIR}/{tag}-{i}.png")
        ow = await pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        print("horizontal overflow px:", ow)
        print("\n".join(msgs[:20]))
        await b.close()
asyncio.run(main())
