"""Observed submission-to-acceptance turnaround from Crossref deposits.

For each journal ISSN we draw a random sample (Crossref `sample=`) of journal
articles first published inside a window and keep those whose metadata contain
BOTH a 'received' and an 'accepted' assertion. Output is observed history, NOT
a guarantee of future timelines.
"""
import json, sys, time, re
import requests, pandas as pd

BASE = "https://api.crossref.org/works"
WINDOW = ("2025-01-01", "2026-09-30")

def parse(s):
    try:
        return pd.to_datetime(re.sub(r"\s+", " ", s.strip()), dayfirst=False, errors="coerce")
    except Exception:
        return pd.NaT

def fetch(issn, n_samples=3, window=WINDOW, doc_type="journal-article"):
    rows, seen = [], set()
    for _ in range(n_samples):
        params = {"filter": f"issn:{issn},from-pub-date:{window[0]},until-pub-date:{window[1]},type:{doc_type}",
                  "sample": 100, "select": "DOI,assertion,issued,title,container-title,page,article-number"}
        for attempt in range(4):
            try:
                r = requests.get(BASE, params=params, timeout=60)
                if r.status_code == 200: break
            except requests.RequestException:
                pass
            time.sleep(2 ** attempt)
        else:
            continue
        for it in r.json()["message"]["items"]:
            if it["DOI"] in seen: continue
            seen.add(it["DOI"])
            a = {x["name"].lower(): x.get("value") for x in it.get("assertion", []) if "name" in x}
            rows.append(dict(issn=issn, doi=it["DOI"], has_dates=("received" in a and "accepted" in a),
                             received=a.get("received"), accepted=a.get("accepted"),
                             revised=a.get("revised"), issued=str(it.get("issued", {}).get("date-parts"))))
    return pd.DataFrame(rows)

def summarize(df):
    if df.empty:
        return dict(sampled=0, with_dates=0), df.assign(days=pd.Series(dtype=float))
    d = df[df.has_dates].copy()
    out = dict(sampled=len(df), with_dates=0)
    if d.empty:
        return out, d.assign(days=pd.Series(dtype=float))
    d["r"] = pd.to_datetime(d.received.map(parse), errors="coerce")
    d["a"] = pd.to_datetime(d.accepted.map(parse), errors="coerce")
    d = d.dropna(subset=["r", "a"])
    d["days"] = (d.a - d.r).dt.days
    d = d[d.days.between(0, 1500)]
    out["with_dates"] = len(d)
    if len(d) >= 5:
        out.update(median=float(d.days.median()), q25=float(d.days.quantile(.25)), q75=float(d.days.quantile(.75)),
                   min=int(d.days.min()), frac_le72=float((d.days <= 72).mean()), n_le72=int((d.days <= 72).sum()))
    return out, d

if __name__ == "__main__":
    cands = json.load(open(sys.argv[1]))
    allrows, summ = [], []
    for name, issn in cands.items():
        df = fetch(issn)
        s, d = summarize(df); s.update(journal=name, issn=issn)
        summ.append(s); allrows.append(d.assign(journal=name))
        print(s, flush=True)
    pd.DataFrame(summ).to_csv(sys.argv[2], index=False)
    if allrows: pd.concat(allrows).to_csv(sys.argv[2].replace(".csv", "_articles.csv"), index=False)
