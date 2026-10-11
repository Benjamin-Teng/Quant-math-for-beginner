#!/usr/bin/env python3
"""Fail if banned terms appear in sources, labs, docs or the built site.

The rule and its scope are in CLAUDE.md ("Intellectual property"). BANNED holds tripwire terms for that scope, not
the rule itself: a hit asks where the text came from. Add a term to BANNED when a new one turns up. If a citation the
rule allows needs one of them (for example the publisher of a public document; LM1 cites the GIPS standards), add a
narrow exact-phrase exception to this script. Run from the repository root:

    uv run python build/qa/check_terms.py          # exit 1 and list hits if any banned term is found

Notebooks are scanned in their cell sources and text outputs only, because base64 images match short
terms by accident.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANNED = re.compile(r"\bCFA\b|Chartered Financial Analyst|candidate should be able", re.IGNORECASE)
SKIP_DIRS = {"node_modules", ".venv", ".git", ".claude", "dist", "__pycache__", ".ipynb_checkpoints"}   # .claude: agent worktrees
SUFFIXES = {".md", ".py", ".js", ".css", ".html", ".yaml", ".yml", ".json", ".txt", ".sh", ".ipynb"}

def text_of(p: Path) -> str:
    s = p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix != ".ipynb":
        return s
    nb, parts = json.loads(s), []
    for c in nb.get("cells", []):
        parts.append("".join(c["source"]) if isinstance(c["source"], list) else c["source"])
        for o in c.get("outputs", []):
            t = o.get("text") or o.get("data", {}).get("text/plain") or ""
            parts.append("".join(t) if isinstance(t, list) else t)
    return "\n".join(parts)

hits = []
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix not in SUFFIXES or SKIP_DIRS & set(p.parts) or p.resolve() == Path(__file__).resolve():
        continue
    for i, line in enumerate(text_of(p).splitlines(), 1):
        if BANNED.search(line):
            hits.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()[:120]}")
if hits:
    print("banned terms found:\n" + "\n".join(hits))
    sys.exit(1)
print("check_terms: clean")
