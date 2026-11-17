"""Observed received->accepted days from Crossref assertions (Springer Nature, Wiley and some others deposit them) for recent articles of candidate journals.
OBSERVED HISTORY ONLY: survivor-biased (accepted papers only), says nothing about JCR quartile or about the chance of acceptance. Usage: python journal_census_v2.py"""
import requests, time, json, numpy as np, pandas as pd, sys
J = {"Software: Practice and Experience (Wiley)": "0038-0644", "Concurrency and Computation: Practice and Experience (Wiley)": "1532-0626", "Computational and Applied Mathematics (Springer)": "2238-3603", "J Brazilian Soc Mech Sci Eng (Springer)": "1678-5878", "Archive of Applied Mechanics (Springer)": "0939-1533", "Acta Mechanica (Springer)": "0001-5970", "Computational Mechanics (Springer)": "0178-7675", "Meccanica (Springer)": "0025-6455", "Applied Mathematics and Mechanics English (Springer)": "0253-4827", "Engineering with Computers (Springer)": "0177-0667", "Numerical Algorithms (Springer)": "1017-1398", "Journal of Mechanical Science and Technology (Springer)": "1738-494X", "Acta Mechanica Sinica (Springer)": "0567-7718", "Computational Optimization and Applications (Springer)": "0926-6003", "Engineering Optimization (T&F)": "0305-215X", "Int J Numerical Methods for Heat & Fluid Flow (Emerald)": "0961-5539", "Engineering Computations (Emerald)": "0264-4401", "Int J Uncertainty Quantification (Begell)": "2152-5080"}
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
json.dump(out, open("../results/journal_census_v3.json", "w"), indent=1)
