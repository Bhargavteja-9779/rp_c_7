"""Word version of the main manuscript: resolve \\cref/\\Cref and \\ref from main.aux/supplement.aux, expand macros (already in macros.tex), use PNG figures, run pandoc, post-process."""
import re, subprocess, pathlib, sys, shutil
P = pathlib.Path(__file__).resolve().parent; aux = {}
for f in ("main.aux", "supplement.aux"):
    for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", (P / f).read_text()): aux[m.group(1)] = m.group(2)
PREF = {"sec": "Section", "fig": "Fig.", "tab": "Table", "eq": "Eq.", "alg": "Algorithm", "prop": "Proposition"}
def ref(lab, cap):
    kind = lab.split(":")[0]; num = aux.get(lab, "?"); w = PREF.get(kind, ""); w = w if not cap else w; return f"{w} {num}".strip()
def expand(tex):
    tex = re.sub(r"\\[cC]ref\{([^}]+)\}", lambda m: ", ".join(ref(l, True) for l in m.group(1).split(",")), tex); tex = re.sub(r"\\eqref\{([^}]+)\}", lambda m: f"({aux.get(m.group(1), '?')})", tex)
    tex = re.sub(r"\\ref\{([^}]+)\}", lambda m: aux.get(m.group(1), "?"), tex); tex = tex.replace("\\Cref", "\\cref"); return tex
def flatten(path):
    t = path.read_text()
    def inc(m):
        f = m.group(1); f = f if f.endswith(".tex") else f + ".tex"; q = P / f
        return flatten(q) if q.exists() else ""
    return re.sub(r"\\input\{([^}]+)\}", inc, t)
body = flatten(P / "main.tex"); body = re.sub(r"\\externaldocument\{[^}]*\}", "", body); body = re.sub(r"\.pdf\}", ".png}", body); body = expand(body)
body = re.sub(r"\\newtheorem\{[^}]*\}\{[^}]*\}", "", body); body = body.replace("\\begin{algorithm}[t]", "\\begin{algorithm}").replace("\\KwIn", "\\textbf{Input:} ").replace("\\ForEach", "\\textbf{for each} ").replace("\\Return", "\\textbf{return} ")
(P / "main_word.tex").write_text(body)
subprocess.run(["pandoc", "main_word.tex", "-f", "latex", "-t", "docx", "-o", "main_word.docx", "--bibliography=references.bib", "--citeproc", "--resource-path=.", "--number-sections"], cwd=P, check=True)
subprocess.run([sys.executable, "postprocess_docx.py", "main_word.docx"], cwd=P, check=True)
