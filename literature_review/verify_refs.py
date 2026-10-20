"""Resolve candidate references against Crossref (title + first author); print best hit for human check."""
import requests, sys, json
Q = [
("Non-intrusive reduced order modeling of nonlinear problems using neural networks","Hesthaven"),
("Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators","Lu"),
("Model reduction and neural networks for parametric PDEs","Bhattacharya"),
("Neural operator: learning maps between function spaces with applications to PDEs","Kovachki"),
("The cost-accuracy trade-off in operator learning with neural networks","de Hoop"),
("Weak baselines and reporting biases lead to overoptimism in machine learning for fluid-related partial differential equations","McGreivy"),
("A deep learning approach to reduced order modelling of parameter dependent partial differential equations","Franco"),
("A comprehensive and fair comparison of two neural operators (with practical extensions) based on FAIR data","Lu"),
("Can physics-informed neural networks beat the finite element method?","Grossmann"),
("Approximation of high-dimensional parametric PDEs","Cohen"),
("Reduced basis methods: success, limitations and future challenges","Ohlberger"),
("Model reduction of dynamical systems on nonlinear manifolds using deep convolutional autoencoders","Lee"),
("Decay of the Kolmogorov N-width for wave problems","Greif"),
("Learning in latent spaces improves the predictive accuracy of deep neural operators","Kontolati"),
("Statistical comparisons of classifiers over multiple data sets","Demsar"),
("Accounting for variance in machine learning benchmarks","Bouthillier"),
("Show your work: improved reporting of experimental results","Dodge"),
("Characterizing possible failure modes in physics-informed neural networks","Krishnapriyan"),
("Physics-informed neural networks: a deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations","Raissi"),
("Reduced Basis Methods for Partial Differential Equations: An Introduction","Quarteroni"),
("Time for a change: a tutorial for comparing multiple classifiers through Bayesian analysis","Benavoli"),
("Calibrated uncertainty quantification for operator learning via conformal prediction","Ma"),
("The impact of data splitting methods on machine learning models: a case study","Joseph"),
("Gaussian processes for machine learning","Rasmussen"),
("Optimal approximation of parametric PDE solution manifolds Kolmogorov n-width","Cohen"),
]
res=[]
for t,a in Q:
    import time
    for _t in range(6):
        resp=requests.get("https://api.crossref.org/works",params={"query.bibliographic":t,"query.author":a,"rows":2,"select":"DOI,title,author,issued,container-title,type,volume,issue,page,article-number,publisher"},timeout=60)
        if resp.text.startswith("{"): break
        time.sleep(3*(_t+1))
    r=resp.json()["message"]["items"]
    for it in r[:2]:
        print(f"Q: {t[:70]} [{a}]\n   -> {it.get('title',[''])[0][:90]} | {', '.join((x.get('family','') for x in it.get('author',[])[:3]))} | {it.get('issued',{}).get('date-parts',[[None]])[0][0]} | {(it.get('container-title') or [''])[0]} | vol {it.get('volume')} pp {it.get('page') or it.get('article-number')} | {it['DOI']}")
        res.append(dict(query=t,hit=it))
json.dump(res,open("literature_review/crossref_ref_hits.json","w"),indent=1)
