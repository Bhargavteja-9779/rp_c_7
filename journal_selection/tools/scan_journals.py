"""Broad landscape scan: enumerate journals via Crossref topical queries, keep established
non-MDPI publishers, sample articles, compute observed submission->acceptance turnaround."""
import requests, json, time, sys, pandas as pd
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "tools")
from crossref_turnaround import fetch, summarize

QUERIES = ["artificial intelligence","machine learning","neural","data mining","signal processing","pattern recognition",
 "computer vision","image","remote sensing","biomedical engineering","medical informatics","bioinformatics","computational",
 "intelligent systems","soft computing","optimization","control","robotics","sensors","internet of things","cybersecurity",
 "information systems","software","computing","statistics","applied mathematics","energy","power systems","industrial",
 "manufacturing","transportation","environmental","water","neuroscience","health","materials","engineering","networks",
 "data science","big data","knowledge","decision","fuzzy","evolutionary","simulation","modelling","analytics","education technology"]
OK_PUB = ["springer","wiley","taylor","oxford","cambridge","sage","iet","institution of engineering","frontiers","peerj","association for computing","de gruyter","world scientific","ios press","nature","biomed central","bmc","plos","royal society","american chemical","iop","aip"]
def enum():
    seen = {}
    for q in QUERIES:
        for off in range(0, 2000, 1000):
            try:
                r = requests.get("https://api.crossref.org/journals", params={"query": q, "rows": 1000, "offset": off}, timeout=60).json()["message"]["items"]
            except Exception as e:
                print("enum fail", q, e); break
            for j in r:
                pub = (j.get("publisher") or "").lower()
                if "mdpi" in pub or not any(p in pub for p in OK_PUB): continue
                if not j.get("ISSN"): continue
                seen[j["ISSN"][0]] = (j["title"], j["publisher"], 0)
            if len(r) < 1000: break
    return seen
def work(item):
    issn, (title, pub, n) = item
    try:
        df = fetch(issn, n_samples=2)
        s, d = summarize(df); s.update(journal=title, publisher=pub, issn=issn, total_dois=n)
        return s
    except Exception as e:
        return dict(journal=title, publisher=pub, issn=issn, err=str(e))
if __name__ == "__main__":
    js = enum(); print("journals enumerated:", len(js), flush=True)
    json.dump(js, open("data/scan_enumerated.json", "w"))
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(work, js.items()))
    pd.DataFrame(res).to_csv("data/scan_v1.csv", index=False)
    print("done", len(res))
