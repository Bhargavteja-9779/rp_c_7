"""Post-process the pandoc Word file: numbered 'Fig. N.' / 'TABLE N' captions, fixed table widths, small table font, equations left as native Word math."""
import sys, re, docx
from docx.shared import Pt, Cm
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
d = docx.Document(sys.argv[1]); sec = d.sections[0]; sec.page_width, sec.page_height = Cm(21.0), Cm(29.7); sec.left_margin = sec.right_margin = Cm(2.0); usable = sec.page_width - sec.left_margin - sec.right_margin
for t in d.tables:
    t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False; lens = [max(len(c.text) for c in col.cells) for col in t.columns]; w = [max(8, min(l, 40)) for l in lens]; tot = sum(w)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); t._tbl.tblPr.append(lay)
    for j, col in enumerate(t.columns):
        for c in col.cells:
            c.width = int(usable * w[j] / tot)
            for p in c.paragraphs:
                for r in p.runs: r.font.size = Pt(7.5)
    for row in t.rows:
        for c in row.cells:
            b = OxmlElement("w:tcBorders")
            for e in ("top", "bottom"): x = OxmlElement(f"w:{e}"); x.set(qn("w:val"), "single"); x.set(qn("w:sz"), "4"); x.set(qn("w:color"), "BBBBBB"); b.append(x)
            c._tc.get_or_add_tcPr().append(b)
# captions: pandoc marks them with style 'Image Caption' / 'Table Caption'
nf = nt = 0
for p in d.paragraphs:
    st = p.style.name
    if st == "Image Caption" and not re.match(r"^Fig\.", p.text): nf += 1; p.runs[0].text = f"Fig. {nf}. " + p.runs[0].text if p.runs else None
    elif st == "Table Caption" and not re.match(r"^TABLE", p.text): nt += 1; p.runs[0].text = f"TABLE {nt}. " + p.runs[0].text if p.runs else None
for p in d.paragraphs:
    for r in p.runs:
        if r.font.size is None and p.style.name in ("Body Text", "First Paragraph", "Compact"): r.font.size = Pt(10.5)
d.save(sys.argv[1]); print("figures numbered:", nf, "tables numbered:", nt)
