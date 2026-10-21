import requests, time, re, xml.etree.ElementTree as ET
def cr(title, author, year=None):
    for t in range(6):
        r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": f"{title} {author}", "rows": 3, "select": "DOI,title,author,issued,container-title,volume,issue,page,article-number"}, timeout=60)
        if r.text.startswith("{"): break
        time.sleep(3 * (t + 1))
    for it in r.json()["message"]["items"][:3]:
        print(f"  CR: {it.get('title',[''])[0][:80]} | {', '.join(x.get('family','') for x in it.get('author',[])[:3])} | {it.get('issued',{}).get('date-parts',[[None]])[0][0]} | {(it.get('container-title') or [''])[0][:45]} | v{it.get('volume')} n{it.get('issue')} pp{it.get('page') or it.get('article-number')} | {it['DOI']}")
print("--- Crossref")
for t, a in [("Weak baselines and reporting biases lead to overoptimism in machine learning for fluid-related partial differential equations", "McGreivy Hakim"),
             ("A deep learning approach to reduced order modelling of parameter dependent partial differential equations", "Franco Manzoni Zunino"),
             ("A comprehensive and fair comparison of two neural operators", "Lu Meng Cai Karniadakis"),
             ("Can physics-informed neural networks beat the finite element method", "Grossmann Komorowska Latz Schonlieb"),
             ("Approximation of high-dimensional parametric PDEs", "Cohen DeVore Acta Numerica"),
             ("Individual comparisons by ranking methods", "Wilcoxon"),
             ("A simple sequentially rejective multiple test procedure", "Holm"),
             ("SciPy 1.0: fundamental algorithms for scientific computing in Python", "Virtanen"),
             ("The impact of data splitting methods on machine learning models", "MLCSE Springer 2025"),
             ("Gaussian Processes for Machine Learning", "Rasmussen Williams MIT Press 2006")]:
    print(t[:70]); cr(t, a)
print("--- arXiv")
ids = ["2010.08895", "2210.07182", "2109.01050", "2103.03098", "1412.6980", "1912.01703", "2111.05512"]
x = requests.get("https://export.arxiv.org/api/query", params={"id_list": ",".join(ids), "max_results": 10}, timeout=60).text
ns = {"a": "http://www.w3.org/2005/Atom"}
for e in ET.fromstring(x).findall("a:entry", ns):
    print(" ", e.find("a:id", ns).text.split("/abs/")[-1], "|", re.sub(r"\s+", " ", e.find("a:title", ns).text)[:90], "|", ", ".join(a.find("a:name", ns).text for a in e.findall("a:author", ns)[:3]), "|", e.find("a:published", ns).text[:4])
