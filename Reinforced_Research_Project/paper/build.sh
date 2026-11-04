#!/bin/bash
# Build main + supplement PDFs, Word version, and run the layout checks.  Usage: bash build.sh [--no-aggregate]
set -e; cd "$(dirname "$0")"
if [ "$1" != "--no-aggregate" ]; then python ../code/experiments/aggregate.py; fi
python - <<'PY'
import subprocess, pathlib
root = pathlib.Path('..').resolve(); out = []
for p in (root.parent / 'research_design/deviations.md', root / 'research_design/deviations_v2.md'):
    t = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', '--wrap=none', str(p)], capture_output=True, text=True).stdout
    out.append(t.replace('\\section{', '\\subsection*{').replace('\\subsection{', '\\subsubsection*{'))
import re
txt = '\n'.join(out)
txt = re.sub(r'\\texttt\{([^}]*)\}', lambda m: '\\texttt{' + m.group(1).replace('/', '/\\allowbreak{}').replace('\\_', '\\_\\allowbreak{}') + '}', txt)
pathlib.Path('tables/deviations.tex').write_text(txt)
PY
for i in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error supplement.tex >/dev/null || true; pdflatex -interaction=nonstopmode -halt-on-error main.tex > build_main.log || { tail -30 build_main.log; exit 1; }; bibtex main >/dev/null 2>&1 || true; done
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build_main.log; pdflatex -interaction=nonstopmode -halt-on-error supplement.tex > build_supp.log; pdflatex -interaction=nonstopmode -halt-on-error main.tex > build_main.log
bash check_build.sh
