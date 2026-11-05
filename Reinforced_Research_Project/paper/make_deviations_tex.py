"""Convert the pipe tables of the deviation logs into itemised LaTeX (instead of a wide longtable) -> tables/deviations.tex"""
import re, pathlib, subprocess
root = pathlib.Path(__file__).resolve().parents[1]; out = []
def md_inline(s):
    tex = subprocess.run(["pandoc", "-f", "markdown", "-t", "latex", "--wrap=none"], input=s, capture_output=True, text=True).stdout.strip()
    tex = re.sub(r"\\texttt\{([^}]*)\}", lambda m: "\\texttt{" + m.group(1).replace("/", "/\\allowbreak{}").replace("\\_", "\\_\\allowbreak{}") + "}", tex); return tex
for p, title in ((root.parent / "research_design/deviations.md", "First stage (original 16 problems)"), (root / "research_design/deviations_v2.md", "Later stages (replication, controls, tool evaluation)")):
    out.append("\\subsection*{%s}\n\\begin{description}\\setlength{\\itemsep}{2pt}" % title)
    for line in p.read_text().splitlines():
        if line.startswith("|") and not line.startswith("|---") and not line.startswith("| #"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5: out.append("\\item[%s] \\textbf{%s} (%s). %s \\emph{Effect:} %s" % (md_inline(cells[0]), md_inline(cells[1]), md_inline(cells[2]), md_inline(cells[3]), md_inline(cells[4])))
    # sections written as headings (V9, V10 ...)
    txt = p.read_text(); 
    for m in re.finditer(r"^## (V\d+[^\n]*)\n(.*?)(?=^## |\Z)", txt, re.S | re.M):
        out.append("\\item[%s] %s" % (md_inline(m.group(1).split(" — ")[0]), md_inline(m.group(1).split(" — ", 1)[-1] + ". " + " ".join(m.group(2).split()))))
    out.append("\\end{description}")
(root / "paper/tables/deviations.tex").write_text("\n".join(out) + "\n"); print(len("\n".join(out)))
