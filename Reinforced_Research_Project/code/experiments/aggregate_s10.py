"""Part 6 of aggregate.py: Stage 10 (results/s10; protocol_addendum_v3.5.md): the pole-aware rational member. Macros prefix 'sr'."""
import json, pandas as pd


def part6(ag):
    R, mac, fi, fc, fd, fp, fs, tex_table = ag.R, ag.mac, ag.fi, ag.fc, ag.fd, ag.fp, ag.fs, ag.tex_table; S = R / "s10"; pm = lambda m: "met" if m else "not met"
    if not (S / "criteria.json").exists() or not (S / "F_cells_with_net.csv").exists(): return
    C = json.load(open(S / "criteria.json")); r1, r2, r3, r4, r5, r6 = (C.get(k) for k in ("R1", "R2", "R3", "R4", "R5", "R6"))
    if r6 is None: return
    mac("sr_one_k", fc(r1["n_half"])); mac("sr_one_n", fc(r1["n_cells"])); mac("sr_one_verdict", pm(r1["met"])); mac("sr_two_worse", fc(r2["n_worse10"])); mac("sr_two_verdict", pm(r2["met"])); mac("sr_three_median", fd(r3["median_regret"], 2)); mac("sr_three_share", fp(r3["share_le2"])); mac("sr_three_verdict", pm(r3["met"]))
    mac("sr_four_k", fc(r4["net_better25"])); mac("sr_four_n", fc(r4["n_cells"])); mac("sr_four_verdict", pm(r4["met"])); mac("sr_five_new", fc(r5["usable_new"])); mac("sr_five_old", fc(r5["usable_old"])); mac("sr_five_n", fc(r5["n_cells"])); mac("sr_five_verdict", pm(r5["met"]))
    mac("sr_six_n", fi(r6["n_problems"])); mac("sr_six_median", fd(r6["median_ratio"], 2)); mac("sr_six_worse", fc(r6["n_worse10"])); mac("sr_six_verdict", pm(r6["met"])); mac("sr_met_count", fc(sum(bool(x["met"]) for x in (r1, r2, r3, r4, r5, r6))))
    h = C["R7_H"]; mac("sr_h_better", fc(h["n_better25"])); mac("sr_h_selected_n", fc(h["n_cells_rat_selected"])); Hc = pd.read_csv(S / "H_cells.csv"); hh = Hc[Hc.instance == "helmholtz_L1"].iloc[0]; mac("sr_h_helm_new", fd(hh.new, 2)); mac("sr_h_helm_old", fd(hh.old, 2))
    mac("sr_rat_share", fp(C["R8_F"]["median_rat_seconds_share"], 1)); mac("sr_rat_sec_tentwentyfour", fd(C["R8_F"]["median_rat_seconds_N1024"], 0))
    Q = pd.read_csv(S / "F_cells_with_net.csv"); n_better = int((Q.new / Q.old < 0.8).sum()); mac("sr_f_better_fifth", fc(n_better)); mac("sr_f_n", fc(len(Q) + 4))
    L = []
    for _, r in Q.iterrows(): L.append({"Problem": "\\texttt{" + r.instance.replace("_", "\\_") + "}", "$N$": int(r.N), "Old pool": fs(r.old, 1), "With rational": fs(r.new, 1), "Tuned net": fs(r.net, 1), "Rational chosen": f"{int(r.n_sel_rat)} of 3"})
    tex_table("sr_cells", pd.DataFrame(L), colfmt="lrrrrr")
    F = pd.read_csv(S / "F_cells.csv"); b = lambda inst, N: F[(F.instance == inst) & (F.N == N)].iloc[0]
    for inst, N, nm in (("acoustic_cavity_L1", 256, "a256"), ("acoustic_cavity_L1", 1024, "a1024"), ("beam_frf_L1", 1024, "b1024")): r = b(inst, N); mac(f"sr_{nm}_new".replace("256", "_twofiftysix").replace("1024", "_tentwentyfour"), fs(r.new, 1)); mac(f"sr_{nm}_old".replace("256", "_twofiftysix").replace("1024", "_tentwentyfour"), fs(r.old, 1))


def problems_table_s10(ag):
    import sys
    sys.path.insert(0, str(ag.ROOT / "code/src")); from surrogate_bench.problems_tp4 import build_suite_frf
    L = [{"Problem": "\\texttt{" + n.replace("_", "\\_") + "}", "$p$": P.p, "$m$": P.m, "Description": P.description.replace("scikit-fem ", "").replace("_", "\\_")} for n, P in build_suite_frf().items()]
    ag.tex_table("sr_problems", pd.DataFrame(L), colfmt="lrrp{7.2cm}")
