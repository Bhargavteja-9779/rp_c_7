"""Deterministic full harvest of Crossref records (cursor paging) for one ISSN; compute
submission->acceptance. Usage: full_harvest.py ISSN FROM TO OUT.csv"""
import sys, requests, pandas as pd, re, time
issn, frm, to, out = sys.argv[1:5]
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
def parse(s):
    s = re.sub(r"\s+", " ", s.strip()) if isinstance(s, str) else ""
    for fmt in ("%d %B %Y", "%B %d, %Y", "%Y-%m-%d", "%d %b %Y"):
        try: return pd.to_datetime(s, format=fmt)
        except Exception: pass
    return pd.NaT
cursor, rows = "*", []
while True:
    for _try in range(5):
        resp = requests.get("https://api.crossref.org/works", params={
        "filter": f"issn:{issn},from-pub-date:{frm},until-pub-date:{to},type:journal-article",
        "rows": 500, "cursor": cursor, "select": "DOI,title,assertion,issued,page,article-number"}, timeout=90)
        if resp.status_code == 200 and resp.text.startswith("{"): break
        time.sleep(3 * (_try + 1))
    r = resp.json()["message"]
    if not r["items"]: break
    for it in r["items"]:
        a = {x["name"].lower(): x.get("value") for x in it.get("assertion", []) if "name" in x}
        rows.append(dict(doi=it["DOI"], title=(it.get("title") or [""])[0][:90], received=a.get("received"), accepted=a.get("accepted"),
                         issued=str(it.get("issued", {}).get("date-parts", [[None]])[0])))
    cursor = r["next-cursor"]; time.sleep(.3)
d = pd.DataFrame(rows)
d["r"] = d.received.map(parse); d["a"] = d.accepted.map(parse)
d["days"] = (d.a - d.r).dt.days
d.to_csv(out, index=False)
v = d.dropna(subset=["days"]); v = v[v.days >= 0]
print(f"{issn}: records={len(d)} with_both_dates={len(v)}")
if len(v):
    print(v.days.describe(percentiles=[.1,.25,.5,.75,.9]).round(1).to_string())
    print("share <=72:", round((v.days <= 72).mean(), 3), " share <=90:", round((v.days <= 90).mean(), 3), " max:", v.days.max())
