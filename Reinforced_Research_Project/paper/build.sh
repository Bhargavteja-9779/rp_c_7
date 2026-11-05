#!/bin/bash
# Build main + supplement PDFs, Word version, and run the layout checks.  Usage: bash build.sh [--no-aggregate]
set -e; cd "$(dirname "$0")"
if [ "$1" != "--no-aggregate" ]; then python ../code/experiments/aggregate.py; fi
python make_deviations_tex.py
for i in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error supplement.tex >/dev/null || true; pdflatex -interaction=nonstopmode -halt-on-error main.tex > build_main.log || { tail -30 build_main.log; exit 1; }; bibtex main >/dev/null 2>&1 || true; done
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build_main.log; pdflatex -interaction=nonstopmode -halt-on-error supplement.tex > build_supp.log; pdflatex -interaction=nonstopmode -halt-on-error main.tex > build_main.log
bash check_build.sh
