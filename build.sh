#!/usr/bin/env bash
# Build "From Calculus to Kelly".
#   ./build.sh            site -> docs/ (any static host) and dist/artifact/ (claude.ai artifact bundle)
#   ./build.sh --pdf      also render each module to docs/pdf/ (needs: playwright install chromium)
#   ./build.sh --data     first rebuild data/processed and src/data/*.json from data/raw
#   ./build.sh --labs     also regenerate and execute the lab notebooks
set -euo pipefail
cd "$(dirname "$0")"
PDF=0; DATA=0; LABS=0
for a in "$@"; do case "$a" in --pdf) PDF=1;; --data) DATA=1;; --labs) LABS=1;; *) echo "unknown option $a"; exit 2;; esac; done

command -v node >/dev/null || { echo "Node.js is required (KaTeX renders math at build time)"; exit 1; }
[ -d build/node_modules/katex ] || (cd build && npm ci --no-audit --no-fund)

if [ "$DATA" = 1 ]; then
  python3 data/build_series.py        # re-verifies every close against FinMind's spread column
  python3 data/lm03_stats.py > /dev/null
  python3 data/lm03_charts.py
fi

python3 build/build.py --target web
python3 build/build.py --target artifact

if [ "$PDF" = 1 ]; then
  mkdir -p docs/pdf
  python3 build/build.py --list-pdfs | while IFS='|' read -r html pdf title; do
    python3 build/render_pdf.py "file://$PWD/docs/$html" "docs/$pdf" "$title"
    echo "rendered docs/$pdf"
  done
fi

if [ "$LABS" = 1 ]; then
  python3 build/make_lab03.py
  (cd labs/LM03_lab && jupyter nbconvert --to notebook --execute LM03_lab.ipynb --output LM03_lab.ipynb)
fi
echo "done: open docs/index.html"
