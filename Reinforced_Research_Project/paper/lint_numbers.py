"""Lint: report digits typed into sections/*.tex that are not macros, not inside math, not in references/labels/filenames. Protocol constants are allow-listed in lint_allow.txt (one regex per line). Exit code 1 if any remain."""
import re, sys, pathlib
P = pathlib.Path(__file__).resolve().parent; allow = [re.compile(l.strip()) for l in (P / "lint_allow.txt").read_text().splitlines() if l.strip() and not l.startswith("#")] if (P / "lint_allow.txt").exists() else []
bad = []
for f in sorted((P / "sections").glob("*.tex")):
    for i, line in enumerate(re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", lambda m: "\n" * m.group(0).count("\n"), f.read_text(), flags=re.S).splitlines(), 1):
        if line.lstrip().startswith("%"): continue
        if "begin{equation}" in line or "end{equation}" in line or "\\label{eq:" in line: continue
        t = re.sub(r"\$[^$]*\$", " ", line); t = re.sub(r"\\(label|ref|cref|Cref|eqref|cite|input|includegraphics|verbatiminput|texttt|bibliography)\*?(\[[^\]]*\])?\{[^}]*\}", " ", t); t = re.sub(r"\\[A-Za-z]+", " ", t)
        for m in re.finditer(r"(?<![A-Za-z_\-])\d[\d.,]*\d*|\b\d\b", t):
            tok = m.group(0); ctx = t[max(0, m.start() - 25): m.end() + 25]
            if not any(a.search(ctx) for a in allow): bad.append((f.name, i, tok, ctx.strip()))
for b in bad: print(f"{b[0]}:{b[1]}: {b[2]!r}  ...{b[3]}...")
print(f"typed numbers not allow-listed: {len(bad)}"); sys.exit(1 if bad else 0)
