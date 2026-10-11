"""List the displayed equations of a page that scroll sideways at a given viewport width.

Usage:
    uv run python build/qa/display_scroll.py <html path or URL> [<more pages> ...] [width] [--width 400]
        [--tolerance 2] [--fail]

The default width is 400 px (a phone). Like build/qa/overflow.py, each page is a file path or a URL. A bare number
among the arguments is the width, so ``display_scroll.py dist/preview/lm/lm08.html 400`` works as it does for
overflow.py; options may stand before or after the pages and the number. Two different widths (a bare number and
``--width``, or two bare numbers) are an error (exit 2), as is a negative ``--tolerance``.

For every ``.katex-display`` element whose ``scrollWidth`` exceeds its ``clientWidth`` by more than ``--tolerance`` px
(default 2, so a rounding overflow of a pixel or two is ignored; 0 lists every one) the report gives the equation tag
(the number in parentheses, if any), the overflow in px, both widths and the first 60 characters of its TeX source
(the MathML annotation, or else the ``aria-label`` that build.py puts on the equation, without its ``\\tag``).
A scrolling display is allowed on screen (book.css gives ``.katex-display`` ``overflow-x: auto``) but is hard to read
on a phone: the cure is a line break (``aligned`` or ``gathered``) in the equation.

Exit code: 1 when ``--fail`` is given and any display scrolls, 2 when a page cannot be opened, otherwise 0.
"""

from __future__ import annotations

import argparse
import asyncio
import io
import sys
from pathlib import Path

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

DEFAULT_TOLERANCE = 2  # px; a display 1-2 px too wide (rounding) does not visibly scroll on a phone

SCRIPT = r"""(tol) => {
  const out = [];
  document.querySelectorAll('.katex-display').forEach((el, i) => {
    if (el.scrollWidth - el.clientWidth <= tol) return;
    const tagEl = el.querySelector('.tag');
    const ann = el.querySelector('annotation[encoding="application/x-tex"]');
    const wrap = el.closest('[role="math"][aria-label]');  // build.py keeps the TeX source in the aria-label
    const src = ann ? ann.textContent : (wrap ? wrap.getAttribute('aria-label') : '');
    out.push({
      index: i + 1,
      tag: tagEl ? tagEl.textContent.trim() : '',
      scroll: el.scrollWidth,
      client: el.clientWidth,
      tex: src.replace(/\\tag\{[^}]*\}/g, '').replace(/\s+/g, ' ').trim().slice(0, 60),
    });
  });
  return { total: document.querySelectorAll('.katex-display').length, rows: out };
}"""


def to_url(target: str) -> str:
    return target if "://" in target else Path(target).resolve().as_uri()


async def scan(targets: list[str], width: int, tolerance: int) -> tuple[int, int]:
    """Print the scrolling displays of every page; return (number of scrolling displays, number of failed pages)."""
    found = failed = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": width, "height": 900})
        for target in targets:
            try:
                await page.goto(to_url(target), wait_until="networkidle")
                await page.wait_for_timeout(500)
                res = await page.evaluate(SCRIPT, tolerance)
            except PlaywrightError as exc:  # a missing file or an unreachable URL
                print(f"{target}: cannot open ({exc})", file=sys.stderr)
                failed += 1
                continue
            rows = res["rows"]
            print(f"{target} at {width} px: {len(rows)} of {res['total']} displays scroll")
            for r in rows:
                tag = r["tag"] or "(no tag)"  # the .tag text already has its parentheses
                over = r["scroll"] - r["client"]
                print(f"  display #{r['index']} {tag} overflows {over} px (scrollWidth {r['scroll']} > "
                      f"clientWidth {r['client']}): {r['tex']}")
            found += len(rows)
        await browser.close()
    return found, failed


def main() -> int:
    ap = argparse.ArgumentParser(description="List displayed equations that scroll sideways at a given width.")
    ap.add_argument("targets", nargs="+", help="HTML paths or URLs; a bare number is the width in px")
    ap.add_argument("--width", type=int, default=None, help="viewport width in px (default 400)")
    ap.add_argument("--tolerance", type=int, default=DEFAULT_TOLERANCE,
                    help=f"ignore an overflow of at most this many px (default {DEFAULT_TOLERANCE}; 0 lists every "
                         "display with scrollWidth > clientWidth)")
    ap.add_argument("--fail", action="store_true", help="exit with code 1 when any display scrolls")
    args = ap.parse_intermixed_args()  # options may come before or after the pages and the bare width
    if args.tolerance < 0:
        ap.error("--tolerance must be 0 or more")
    widths = {int(t) for t in args.targets if t.isdigit()}
    if args.width is not None:
        widths.add(args.width)
    if len(widths) > 1:
        ap.error(f"conflicting widths {sorted(widths)}: give the width once, as a bare number or with --width")
    width = widths.pop() if widths else 400
    if width < 1:
        ap.error("the width must be at least 1 px")
    pages = [t for t in args.targets if not t.isdigit()]
    if not pages:
        ap.error("give at least one page")
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    found, failed = asyncio.run(scan(pages, width, args.tolerance))
    if failed:
        return 2
    return 1 if args.fail and found else 0


if __name__ == "__main__":
    sys.exit(main())
