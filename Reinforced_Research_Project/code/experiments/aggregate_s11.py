"""Part 7 of aggregate.py: Stage 11 (results/s11; protocol_addendum_v3.6.md): pole deflation on fresh problems. Macros prefix 'sd'."""
import json, pandas as pd


def part7(ag):
    R, mac, fi, fc, fd, fp, fs, tex_table = ag.R, ag.mac, ag.fi, ag.fc, ag.fd, ag.fp, ag.fs, ag.tex_table; S = R / "s11"; pm = lambda m: "met" if m else "not met"
    if not (S / "criteria.json").exists() or not (S / "F_cells_with_nets.csv").exists(): return
    C = json.load(open(S / "criteria.json")); d1, d2, d3, d4, d5, d6, d7, d8 = (C.get(k) for k in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"))
    if d8 is None: return
    mac("sd_one_k", fc(d1["n_half"])); mac("sd_one_n", fc(d1["n_cells"])); mac("sd_one_verdict", pm(d1["met"])); mac("sd_two_worse", fc(d2["n_worse10"])); mac("sd_two_verdict", pm(d2["met"])); mac("sd_three_median", fd(d3["median_regret"], 2)); mac("sd_three_verdict", pm(d3["met"]))
    mac("sd_four_new", fc(d4["usable_new"])); mac("sd_four_old", fc(d4["usable_old"])); mac("sd_four_n", fc(d4["n_cells"])); mac("sd_four_verdict", pm(d4["met"]))
    mac("sd_five_better", fc(d5["dnet_better25"])); mac("sd_five_worse", fc(d5["dnet_worse25"])); mac("sd_five_verdict", pm(d5["met"])); mac("sd_six_best", fc(d6["usable_best"])); mac("sd_six_verdict", pm(d6["met"])); mac("sd_seven_k", fc(d7["net_better25"])); mac("sd_seven_verdict", pm(d7["met"]))
    mac("sd_eight_n", fi(d8["n_problems"])); mac("sd_eight_median", fd(d8["median_ratio"], 2)); mac("sd_eight_worse", fc(d8["n_worse10"])); mac("sd_eight_verdict", pm(d8["met"])); mac("sd_met_count", fc(sum(bool(x["met"]) for x in (d1, d2, d3, d4, d5, d6, d7, d8))))
    F = pd.read_csv(S / "F_cells.csv"); r = F[(F.instance == "mdk_chain_L1") & (F.N == 1024)].iloc[0]; mac("sd_chain_new", fs(r.new, 1)); mac("sd_chain_old", fs(r.old, 1)); r = F[(F.instance == "mdk_chain_L1") & (F.N == 256)].iloc[0]; mac("sd_chain256_new", fd(r.new, 3)); mac("sd_chain256_old", fd(r.old, 3))
    Q = pd.read_csv(S / "F_cells_with_nets.csv"); L = []
    for _, r in Q.iterrows(): L.append({"Problem": "\\texttt{" + r.instance.replace("_", "\\_") + "}", "$N$": int(r.N), "Old pool": fs(r.old, 1), "With deflated": fs(r.new, 1), "Plain net": fs(r.net, 1), "Deflated net": fs(r.dnet, 1)})
    tex_table("sd_cells", pd.DataFrame(L), colfmt="lrrrrr")
    h = C["D9_H"]; mac("sd_h_better", fc(h["n_better25"])); mac("sd_h_selected_n", fc(len(h["selected_instances"])))


def problems_table_s11(ag):
    import sys
    sys.path.insert(0, str(ag.ROOT / "code/src")); from surrogate_bench.problems_tp5 import build_suite_frf2
    L = [{"Problem": "\\texttt{" + n.replace("_", "\\_") + "}", "$p$": P.p, "$m$": P.m, "Description": P.description.replace("scikit-fem ", "").replace("_", "\\_")} for n, P in build_suite_frf2().items()]
    ag.tex_table("sd_problems", pd.DataFrame(L), colfmt="lrrp{7.2cm}")
