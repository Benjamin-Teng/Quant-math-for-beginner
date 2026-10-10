#!/usr/bin/env python3
"""Fail if a PDF was shrunk to fit: Chromium scales the whole printed document down when any element is wider than
the page area, which makes the text smaller and the page count look lower than it is.

    uv run python build/qa/pdf_scale.py docs/pdf/*.pdf     # exit 1 and list every shrunk PDF

Chromium's PDFs map CSS pixels to points with a 300-dpi matrix (0.24) and a page scale of 300/96 = 3.125 at 100%;
a shrunk document has a smaller page scale. Find what sticks out with print media at the A4 text width (680 px).
"""
import re
import sys
import zlib
from pathlib import Path

FULL = 300 / 96
bad = []
for path in sys.argv[1:]:
    data = Path(path).read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    scales: dict[float, int] = {}
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL):
        try:
            s = zlib.decompress(m.group(1))
        except zlib.error:
            continue
        for a in re.findall(rb"([\d.]+) 0 0 [\d.]+ [-\d.]+ [-\d.]+ cm", s[:400]):
            if float(a) > 1:
                scales[float(a)] = scales.get(float(a), 0) + 1
    scale = max(scales, key=lambda k: scales[k]) if scales else FULL
    shrunk = scale < FULL * (1 - 1e-4)
    print(f"{path}: {pages} pages, scale {scale / FULL:.4f}" + ("  SHRUNK: something is wider than the page" if shrunk else ""))
    if shrunk:
        bad.append(path)
sys.exit(1 if bad else 0)
