"""Observed received->accepted days from Crossref assertions (Springer Nature, Wiley and some others deposit them) for recent articles of candidate journals.
OBSERVED HISTORY ONLY: survivor-biased (accepted papers only), says nothing about JCR quartile or about the chance of acceptance. Usage: python journal_census_v2.py"""
import requests, time, json, numpy as np, pandas as pd, sys
J = {"Structural and Multidisciplinary Optimization": "1615-147X", "Neural Computing and Applications": "0941-0643", "Computational Mechanics": "0178-7675", "Journal of Scientific Computing": "0885-7474", "Statistics and Computing": "0960-3174",
     "Scientific Reports": "2045-2322", "Engineering with Computers": "0177-0667", "Machine Learning for Computational Science and Engineering": "2731-6785", "Int J Numer Meth Eng (Wiley)": "0029-5981", "Applied Intelligence": "0924-669X",
     "Computational Geosciences": "1420-0597", "Advances in Computational Mathematics": "1019-7168", "Journal of Intelligent Manufacturing": "0956-5515", "Soft Computing": "1432-7643", "Frontiers in Physics": "2296-424X", "Frontiers in Artificial Intelligence": "2624-8212",
     "Computational Particle Mechanics": "2196-4378", "Acta Mechanica Sinica": "0567-7718", "Applied Mathematical Modelling (Elsevier)": "0307-904X", "Advances in Engineering Software (Elsevier)": "0965-9978", "SoftwareX (Elsevier)": "2352-7110"}
H = {"User-Agent": "research-turnaround-census (mailto:none)"}
def parse(d):
    try: return pd.to_datetime(d, errors="coerce")
    except Exception: return pd.NaT
out = {}
for name, issn in J.items():
    rows = []; cur = "*"
    for _ in range(3):
        try: r = requests.get("https://api.crossref.org/works", params={"filter": f"issn:{issn},from-pub-date:2025-01-01,type:journal-article", "rows": 200, "cursor": cur, "select": "DOI,assertion,issued"}, headers=H, timeout=60).json()["message"]
        except Exception as e: break
        for it in r.get("items", []):
            a = {x.get("name"): x.get("value") for x in it.get("assertion", []) if x.get("name") in ("received", "accepted")}
            if "received" in a and "accepted" in a: rows.append((parse(a["accepted"]) - parse(a["received"])).days)
        cur = r.get("next-cursor")
        if not r.get("items"): break
        time.sleep(1)
    d = np.array([x for x in rows if x is not None and x == x and x >= 0])
    out[name] = dict(issn=issn, n_with_dates=int(len(d)), median=float(np.median(d)) if len(d) else None, q75=float(np.percentile(d, 75)) if len(d) else None, share_le100=float((d <= 100).mean()) if len(d) else None, share_le72=float((d <= 72).mean()) if len(d) else None)
    print(name, out[name], flush=True)
json.dump(out, open("../results/journal_census_v2.json", "w"), indent=1)
