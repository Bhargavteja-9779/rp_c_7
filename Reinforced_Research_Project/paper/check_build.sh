#!/bin/bash
# Layout and reference checks required before calling a build done.
cd "$(dirname "$0")"
echo "main pages: $(pdfinfo main.pdf | awk '/Pages/{print $2}')   supplement pages: $(pdfinfo supplement.pdf | awk '/Pages/{print $2}')"
for f in main supplement; do
  echo "$f: overfull boxes: $(grep -c 'Overfull' $f.log)   undefined refs/citations: $(grep -ci 'undefined' $f.log)   multiply-defined labels: $(grep -c 'multiply defined' $f.log)   LaTeX errors: $(grep -c '^!' $f.log)"
done
echo "macro leakage in text (a backslash-name in the PDF text): $(pdftotext main.pdf - | grep -c '\\\\[A-Za-z]')"
echo "bibtex warnings: $(grep -c Warning main.blg 2>/dev/null)"
