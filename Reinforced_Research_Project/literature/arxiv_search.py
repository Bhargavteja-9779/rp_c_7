import requests, re, time, json, sys, xml.etree.ElementTree as ET
ns={"a":"http://www.w3.org/2005/Atom"}
Q={
"q1 scaling/sample-complexity of operator learning":'all:"neural operator" AND (all:"scaling law" OR all:"sample complexity" OR all:"data scaling")',
"q2 GP / kernel vs neural operator baselines":'(all:"Gaussian process" OR all:"kernel") AND all:"neural operator" AND (all:baseline OR all:benchmark OR all:comparison)',
"q3 POD-GP vs deep nets reduced order":'all:"reduced order" AND all:"Gaussian process" AND (all:"neural network" OR all:autoencoder) AND all:comparison',
"q4 which surrogate to use / selection / meta":'all:surrogate AND all:PDE AND (all:"model selection" OR all:"which" OR all:"when do") AND (all:neural OR all:POD)',
"q5 n-width neural nonlinear approx parametric PDE":'all:"Kolmogorov" AND all:"n-width" AND all:"neural network" AND all:parametric',
"q6 tuning budget fairness SciML":'(all:"hyperparameter" OR all:tuning) AND all:baseline AND (all:"PDE" OR all:"scientific machine learning") AND (all:fair OR all:benchmark)',
"q7 pre-registered / reproducibility ML PDE":'all:"scientific machine learning" AND (all:reproducibility OR all:preregistration OR all:"pre-registered")',
"q8 intrinsic dimension solution manifold predicts":'all:"intrinsic dimension" AND (all:"solution manifold" OR all:"parametric PDE") AND (all:surrogate OR all:neural)',
}
out={}
for k,q in Q.items():
    for t in range(4):
        r=requests.get("https://export.arxiv.org/api/query",params={"search_query":q,"max_results":8,"sortBy":"relevance"},timeout=60)
        if r.status_code==200 and "<feed" in r.text: break
        time.sleep(4*(t+1))
    try: root=ET.fromstring(r.text)
    except Exception: print(k,"FAILED"); continue
    items=[]
    for e in root.findall("a:entry",ns):
        items.append(dict(id=e.find("a:id",ns).text.split("/abs/")[-1],year=e.find("a:published",ns).text[:4],title=re.sub(r"\s+"," ",e.find("a:title",ns).text),abstract=re.sub(r"\s+"," ",e.find("a:summary",ns).text)))
    out[k]=items; print("\n##",k)
    for i in items: print(f"  {i['id']} ({i['year']}) {i['title'][:110]}")
    time.sleep(3)
json.dump(out,open("arxiv_search_results.json","w"),indent=1)
