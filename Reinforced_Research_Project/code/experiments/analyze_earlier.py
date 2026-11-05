#!/usr/bin/env python3
"""Recompute the earlier-stage statistics (Exp A primary, B, A2, E, F, G, G3, H) from the raw job files, with the calls used when the results were first analysed (protocol_addendum_v2.x). Writes to results/rerun_earlier/ so that the committed originals can be diffed."""
import sys, json, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; R = ROOT / "results"; OUT = R / "rerun_earlier"; (OUT / "tables").mkdir(parents=True, exist_ok=True); sys.path.insert(0, str(ROOT / "code/src"))
from surrogate_bench import analysis as A, analysis_v2 as V
dfO, _, _ = A.load(ROOT.parent / "results/raw"); dfA, _, _ = A.load(R / "raw_expA"); df = pd.concat([dfO, dfA], ignore_index=True); W = lambda n, o: json.dump(o, open(OUT / n, "w"), indent=1, default=float)
rep = V.run_all(None, R / "raw_expA", None, None, ROOT / "research_design/frozen_rules_from_v1.json", ROOT.parent / "results/raw", OUT / "expA_primary") if False else None
rb, tb = V.expB(R / "raw_expB", df); W("expB_statistics.json", rb)
r2, _ = V.expA2(R / "raw_expA2", ROOT / "research_design/expA2_selection.json", p0=0.15); W("expA2_statistics.json", r2)
re_, _ = V.expE(R / "raw_expE", df, R / "raw_expD"); W("expE_statistics.json", re_)
rg, _ = V.expG(R / "raw_expG", df); W("expG_statistics.json", rg)
rf, _ = V.expF(R / "raw_expF", df, ["bratu_L1", "bratu_L2", "burgers_L1", "nlheat_L1", "nlheat_L2", "darcy_L1", "heat2d_L1"]); W("expF_statistics.json", rf)
res = {t: V.expH(R / f"raw_exp{t}", df, "err_krr_wide")[0] for t in ("H8", "H32")}; ok = lambda r: r["ratio_quartiles_in_ard_clear"][0.5] <= 3 and r["share_le3"] >= 0.75; m = lambda r: r["ratio_quartiles_in_ard_clear"][0.5]
res["verdict"] = "H-RANGE" if (ok(res["H8"]) or ok(res["H32"])) else ("H-MLII" if (m(res["H8"]) > 3 and m(res["H32"]) > 3) else "mixed"); W("expH_statistics.json", res)
r3, _ = V.expA3(R / "raw_expA3", ROOT / "research_design/expA3_pilot_features.json"); W("expA3_statistics.json", r3)
def same(name):
    a, b = json.load(open(R / name)), json.load(open(OUT / name)); return json.dumps(a, sort_keys=True, default=float) == json.dumps(b, sort_keys=True, default=float)
print({n: same(n) for n in ("expB_statistics.json", "expA2_statistics.json", "expE_statistics.json", "expG_statistics.json", "expF_statistics.json", "expH_statistics.json", "expA3_statistics.json")})
