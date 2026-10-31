#!/usr/bin/env bash
# Build "From Calculus to Kelly". Python runs in the project's uv environment (pyproject.toml + uv.lock).
#   ./build.sh            published site -> docs/ (any static host) and dist/artifact/ (claude.ai artifact bundle)
#   ./build.sh --preview  also build every module, drafts included, into dist/preview/ (local review copy)
#   ./build.sh --pdf      also render each published module to docs/pdf/ (needs: uv run playwright install chromium)
#   ./build.sh --data     first rebuild data/processed and src/data/*.json from data/raw
#   ./build.sh --labs     also regenerate and execute every lab notebook
#   ./build.sh --fetch    first rebuild data/raw/ from FinMind (needs FINMIND_TOKEN) and every lab's data/ folder
# Volume IV's intraday data (one request a day: 5,351 for TAIEX every 5 seconds) are fetched separately with
# data/fetch_intraday.py (data/README.md); --data then also rebuilds data/derived/vol4_rv.csv when the download is complete
# A module is published when its entry in src/syllabus.yaml has `status: published` (see AUTHORING.md §11).
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1   # UTF-8 text I/O on every OS (a Windows locale such as cp950 breaks the scripts otherwise)
PDF=0; DATA=0; LABS=0; PREVIEW=0; FETCH=0
for a in "$@"; do case "$a" in --pdf) PDF=1;; --data) DATA=1;; --labs) LABS=1;; --preview) PREVIEW=1;; --fetch) FETCH=1;;
  *) echo "unknown option $a"; exit 2;; esac; done

command -v uv >/dev/null || { echo "uv is required: it installs and runs the locked Python environment (uv sync)"; exit 1; }
command -v node >/dev/null || { echo "Node.js is required (KaTeX renders math at build time)"; exit 1; }
[ -d build/node_modules/katex ] || (cd build && npm ci --no-audit --no-fund)
# Every Python step runs in .venv exactly as uv.lock pins it: --locked refuses a stale lock instead of rewriting it,
# --exact removes anything installed by hand, so an undeclared import fails here rather than on a reader's machine.
uvr() { uv run --locked --exact "$@"; }
py() { uvr python "$@"; }
py -c "" || { echo "uv could not run the locked environment (see its message above: run uv lock after editing pyproject.toml; the first uv sync needs network)"; exit 1; }

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
  data/vol2_series.py           # Volume II sector closes, repaired from the 13:30:00 values (needs data/raw/sectors_close/)
  data/lm08_numbers.py data/lm08_charts.py
  data/lm09_numbers.py data/lm09_charts.py
  data/lm10_numbers.py data/lm10_charts.py
  data/lm11_numbers.py data/lm11_charts.py
  data/lm12_numbers.py data/lm12_charts.py
  data/vol3_series.py           # Volume III TR23: the TAIEX total-return index, checked against the price index
  data/lm13_numbers.py data/lm13_charts.py
  data/lm14_charts.py data/lm14_numbers.py   # the numbers script checks the chart files, so charts run first
  data/lm15_numbers.py data/lm15_charts.py   # the charts script also tests lm15.js in Node against SciPy
  data/lm16_numbers.py data/lm16_charts.py   # U28, from vol2_series.py
  data/lm17_numbers.py data/lm17_charts.py
  data/lm18_numbers.py data/lm18_charts.py
  data/vol4_series.py           # Volume IV TX23: the TX near-month settlement on TR23's dates, checked
  data/vol4_rv.py               # LM26 realized variance (data/derived/vol4_rv.csv) from a complete T5S download
  data/lm19_charts.py data/lm19_numbers.py   # the numbers scripts of LM19-LM23, LM25 and LM26 check the chart files,
  data/lm20_charts.py data/lm20_numbers.py   # so charts run first
  data/lm21_charts.py data/lm21_numbers.py   # U28 from vol2_series.py
  data/lm22_charts.py data/lm22_numbers.py
  data/lm23_charts.py data/lm23_numbers.py   # U28, TR23, LM2's pairs, TX23's F_t
  data/lm24_numbers.py data/lm24_charts.py   # TR23 and U28's halves
  data/lm25_charts.py data/lm25_numbers.py   # TX23 and TR23
  data/lm26_charts.py data/lm26_numbers.py   # raw intraday statistics only when data/raw/intraday/ is present
  data/vol5_series.py           # Volumes V-VI: E5 and the checkpoint funds, checked (needs TR23's calendar)
  data/vol5_rules.py            # the through case: eight rules, costs and wealth on E5
  data/lm27_charts.py data/lm27_numbers.py   # Volume V: charts first (each numbers script checks its chart
  data/lm28_charts.py data/lm28_numbers.py   # files and widget data; the widget checks need Node); E5 and the
  data/lm29_charts.py data/lm29_numbers.py   # through case from vol5_series.py and vol5_rules.py, U28 from
  data/lm30_charts.py data/lm30_numbers.py   # vol2_series.py
  data/lm31_charts.py data/lm31_numbers.py
)
# Raw FinMind data are not committed (licence): fetch them with your token and verify against data/raw_manifest.json.
if [ "$FETCH" = 1 ]; then
  py data/fetch_finmind.py
  py data/make_lab_data.py
fi

if [ "$DATA" = 1 ] || [ "$LABS" = 1 ]; then
  py data/fetch_finmind.py --verify > /dev/null || { echo "data/raw is missing or differs from the manifest: run ./build.sh --fetch"; exit 1; }
fi
if [ "$DATA" = 1 ]; then
  for s in "${DATA_STEPS[@]}"; do
    if [ "$s" = data/vol4_rv.py ] && [ ! -d data/raw/intraday/taiex5s ]; then
      echo "data: $s skipped (no data/raw/intraday/taiex5s/: the committed data/derived/vol4_rv.csv stays)"; continue
    fi
    echo "data: $s"; py "$s" > /dev/null
  done
fi

py build/build.py --target web
py build/build.py --target artifact
[ "$PREVIEW" = 1 ] && py build/build.py --preview

if [ "$PDF" = 1 ]; then
  mkdir -p docs/pdf
  py build/build.py --list-pdfs | while IFS='|' read -r html pdf title; do
    py build/render_pdf.py "docs/$html" "docs/$pdf" "$title"
    py build/qa/pdf_scale.py "docs/$pdf" || { echo "docs/$pdf was shrunk to fit: find what is wider than the page"; exit 1; }
  done
fi

if [ "$LABS" = 1 ]; then
  py data/make_lab_data.py
  for gen in build/make_lab[0-9][0-9].py; do
    nn=${gen#build/make_lab}; nn=${nn%.py}
    py "$gen"
    (cd "labs/LM${nn}_lab" && uvr jupyter nbconvert --to notebook --execute "LM${nn}_lab.ipynb" --output "LM${nn}_lab.ipynb" \
      && uvr jupyter nbconvert --to notebook --inplace --CoalesceStreamsPreprocessor.enabled=True "LM${nn}_lab.ipynb")
    # second pass: merge a print the kernel flushed in two pieces (in one pass the merge would run before execution)
  done
fi
py build/qa/check_terms.py     # intellectual-property tripwires (CLAUDE.md)
echo "done: open docs/index.html"
