#!/usr/bin/env bash
# Build "From Calculus to Kelly".
#   ./build.sh            published site -> docs/ (any static host) and dist/artifact/ (claude.ai artifact bundle)
#   ./build.sh --preview  also build every module, drafts included, into dist/preview/ (local review copy)
#   ./build.sh --pdf      also render each published module to docs/pdf/ (needs: playwright install chromium)
#   ./build.sh --data     first rebuild data/processed and src/data/*.json from data/raw
#   ./build.sh --labs     also regenerate and execute every lab notebook
#   ./build.sh --fetch    first rebuild data/raw/ from FinMind (needs FINMIND_TOKEN) and every lab's data/ folder
# A module is published when its entry in src/syllabus.yaml has `status: published` (see AUTHORING.md §11).
set -euo pipefail
cd "$(dirname "$0")"
PDF=0; DATA=0; LABS=0; PREVIEW=0; FETCH=0
for a in "$@"; do case "$a" in --pdf) PDF=1;; --data) DATA=1;; --labs) LABS=1;; --preview) PREVIEW=1;; --fetch) FETCH=1;;
  *) echo "unknown option $a"; exit 2;; esac; done

command -v node >/dev/null || { echo "Node.js is required (KaTeX renders math at build time)"; exit 1; }
[ -d build/node_modules/katex ] || (cd build && npm ci --no-audit --no-fund)

# Data pipeline in dependency order. Scripts that only print numbers run too, as a check that they still work.
DATA_STEPS=(
  data/build_series.py          # re-verifies every close against FinMind's spread column
  data/lm01_numbers.py data/lm01_charts.py
  data/lm02_case.py data/lm02_numbers.py data/lm02_charts.py
  data/lm03_stats.py data/lm03_numbers.py data/lm03_charts.py
  data/lm04_stats.py data/lm04_numbers.py data/lm04_charts.py
  data/lm05_numbers.py data/lm05_charts.py
  data/lm06_basis.py data/lm06_numbers.py data/lm06_charts.py
  data/lm07_series.py data/lm07_stats.py data/lm07_numbers.py data/lm07_tables.py data/lm07_charts.py
)
# Raw FinMind data are not committed (licence): fetch them with your token and verify against data/raw_manifest.json.
if [ "$FETCH" = 1 ]; then
  python3 data/fetch_finmind.py
  python3 data/make_lab_data.py
fi

if [ "$DATA" = 1 ] || [ "$LABS" = 1 ]; then
  python3 data/fetch_finmind.py --verify > /dev/null || { echo "data/raw is missing or differs from the manifest: run ./build.sh --fetch"; exit 1; }
fi
if [ "$DATA" = 1 ]; then
  for s in "${DATA_STEPS[@]}"; do echo "data: $s"; python3 "$s" > /dev/null; done
fi

python3 build/build.py --target web
python3 build/build.py --target artifact
[ "$PREVIEW" = 1 ] && python3 build/build.py --preview

if [ "$PDF" = 1 ]; then
  mkdir -p docs/pdf
  python3 build/build.py --list-pdfs | while IFS='|' read -r html pdf title; do
    python3 build/render_pdf.py "file://$PWD/docs/$html" "docs/$pdf" "$title"
    echo "rendered docs/$pdf"
  done
fi

if [ "$LABS" = 1 ]; then
  python3 data/make_lab_data.py
  for gen in build/make_lab[0-9][0-9].py; do
    nn=${gen#build/make_lab}; nn=${nn%.py}
    python3 "$gen"
    (cd "labs/LM${nn}_lab" && jupyter nbconvert --to notebook --execute "LM${nn}_lab.ipynb" --output "LM${nn}_lab.ipynb")
  done
fi
python3 build/qa/check_terms.py     # the book cites no certification curriculum (project/PITFALLS.md)
echo "done: open docs/index.html"
