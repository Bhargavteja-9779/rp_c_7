"""Observed received->accepted days from PubMed <History> for PubMed-indexed journals (covers Elsevier titles
that do not deposit dates in Crossref). Usage: pubmed_turnaround.py out.csv"""
import requests, re, sys, time, xml.etree.ElementTree as ET, pandas as pd, datetime as dt
JOURNALS = ["Comput Biol Med","Comput Methods Programs Biomed","Artif Intell Med","Med Image Anal","Neural Netw","Comput Med Imaging Graph","Comput Biol Chem","Neuroimage","Comput Struct Biotechnol J","J Biomed Inform",
            ]
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
def ymd(e):
    try: return dt.date(int(e.find("Year").text), int(e.find("Month").text), int(e.find("Day").text))
    except Exception: return None
rows = []
for j in JOURNALS:
    q = f'"{j}"[Journal] AND ("2025/01/01"[EDAT] : "2026/09/30"[EDAT])'
    try:
        ids = requests.get(E+"esearch.fcgi", params={"db":"pubmed","term":q,"retmax":300,"retmode":"json"}, timeout=60).json()["esearchresult"]["idlist"]
    except Exception as e:
        print(j, "esearch failed (not indexed or throttled)"); time.sleep(1); continue
    if not ids: print(j, "no pubmed records"); continue
    x = requests.get(E+"efetch.fcgi", params={"db":"pubmed","id":",".join(ids),"retmode":"xml"}, timeout=120).text
    try: root = ET.fromstring(x)
    except ET.ParseError:
        print(j, "efetch parse failure"); continue
    n = 0
    for art in root.findall(".//PubmedArticle"):
        h = {p.get("PubStatus"): ymd(p) for p in art.findall(".//History/PubMedPubDate")}
        if h.get("received") and h.get("accepted"):
            rows.append(dict(journal=j, pmid=art.find(".//PMID").text, days=(h["accepted"]-h["received"]).days)); n += 1
    print(j, len(ids), "with dates:", n, flush=True); time.sleep(.4)
d = pd.DataFrame(rows); d.to_csv(sys.argv[1], index=False)
s = d.groupby("journal").days.agg(n="count", median="median", q75=lambda x: x.quantile(.75), le72=lambda x: (x<=72).mean()).round(2)
print(s.to_string())
