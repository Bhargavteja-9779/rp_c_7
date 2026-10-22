"""Observed received->accepted days for a random sample of recent MLST (IOP, ISSN 2632-2153) articles, read from public article pages. Observed history only."""
import requests, re, time, json, random, numpy as np, pandas as pd
H = {"User-Agent": "Mozilla/5.0 (research turnaround audit; low-rate)"}
dois = []; cur = "*"
while len(dois) < 3000:
    for t in range(4):
        r = requests.get("https://api.crossref.org/works", params={"filter": "issn:2632-2153,from-pub-date:2025-07-01,until-pub-date:2026-09-30,type:journal-article", "rows": 500, "cursor": cur, "select": "DOI"}, timeout=90)
        if r.text.startswith("{"): break
        time.sleep(3)
    m = r.json()["message"]; 
    if not m["items"]: break
    dois += [i["DOI"] for i in m["items"]]; cur = m["next-cursor"]
random.seed(0); samp = random.sample(dois, min(150, len(dois))); rows = []
def p(s): return pd.to_datetime(s.strip(), format="%d %B %Y", errors="coerce")
for d in samp:
    try:
        x = requests.get("https://iopscience.iop.org/article/" + d, headers=H, timeout=40)
        if x.status_code != 200: continue
        rc = re.search(r'"dateReceived">([^<]+)<', x.text); ac = re.search(r'"dateAccepted">([^<]+)<', x.text)
        if rc and ac: rows.append(dict(doi=d, received=rc.group(1).strip(), accepted=ac.group(1).strip()))
    except Exception: pass
    time.sleep(0.8)
df = pd.DataFrame(rows); df["days"] = (df.accepted.map(p) - df.received.map(p)).dt.days; df = df.dropna(subset=["days"]); df.to_csv("../results/mlst_turnaround_sample.csv", index=False)
q = df.days.quantile([.25, .5, .75, .9]); out = dict(population_crossref_records=len(dois), sampled=len(samp), with_dates=len(df), median=float(q[.5]), q25=float(q[.25]), q75=float(q[.75]), q90=float(q[.9]), max=int(df.days.max()), min=int(df.days.min()), share_le72=float((df.days <= 72).mean()))
json.dump(out, open("../results/mlst_turnaround_summary.json", "w"), indent=1); print(json.dumps(out, indent=1))
