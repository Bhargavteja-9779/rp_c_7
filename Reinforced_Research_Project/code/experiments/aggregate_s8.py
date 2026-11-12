"""Part 4 of aggregate.py: Stage 8 (results/s8; protocol_addendum_v3.3.md): the expensive 3D problem (E8) and the no-usable-model warning check (U). Macros prefix 'se' / 'su'."""
import json


def part4(ag):
    R, mac, fi, fc, fd, fp, fs = ag.R, ag.mac, ag.fi, ag.fc, ag.fd, ag.fp, ag.fs; S = R / "s8"; pm = lambda m: "met" if m else "not met"
    if (S / "E8.json").exists():
        E = json.load(open(S / "E8.json")); mac("se_tsim", fd(E["t_sim_seconds"], 1)); mac("se_one_regret64", fd(E["E8_1"]["regret64"], 2)); mac("se_one_regret256", fd(E["E8_1"]["regret256"], 2)); mac("se_one_verdict", pm(E["E8_1"]["met"]))
        mac("se_two_verdict", pm(E["E8_2"]["met"])); mac("se_two_warn", fi(E["E8_2"]["n_fits_warning"])); mac("se_err_sixtyfour", fp(E["E8_2"]["err64"], 1)); mac("se_err_twofiftysix", fp(E["E8_2"]["err256"], 2))
        r = E["E8_3"]["ratios"]; mac("se_three_k", fc(E["E8_3"]["n_ok"])); mac("se_three_n", fc(E["E8_3"]["n"])); mac("se_three_verdict", pm(E["E8_3"]["met"])); mac("se_ratio_min", fd(min(r), 2)); mac("se_ratio_max", fd(max(r), 2))
        mac("se_four_k", fc(E["E8_4"]["n_net_better"])); mac("se_four_verdict", pm(E["E8_4"]["met"])); mac("se_net_err", fp(E["E8_4"]["err_net256"], 2)); mac("se_gp_err", fp(E["E8_4"]["err_gp256"], 2)); mac("se_net_sec", fi(E["median_network_seconds"]))
        c = E["cost"]; mac("se_toolsec_with", fi(c["256_with_refit"]["tool_seconds"])); mac("se_toolsec_without", fi(c["256_without_refit"]["tool_seconds"])); mac("se_break_with", fi(c["256_with_refit"]["break_even"])); mac("se_break_without", fi(c["256_without_refit"]["break_even"]))
        mac("se_break_sixtyfour", fi(c["64_with_refit"]["break_even"])); mac("se_solver_h", fd(E["hours_solver_1e4"], 1)); mac("se_surr_h", fd(c["256_with_refit"]["hours_surrogate_1e4"], 2)); mac("se_speedup", fi(E["hours_solver_1e4"] / c["256_with_refit"]["hours_surrogate_1e4"]))
        mac("se_simh_twofiftysix", fd(256 * E["t_sim_seconds"] / 3600, 2)); mac("se_simh_sixtyfour", fd(64 * E["t_sim_seconds"] / 3600, 2))
        mac("se_met_count", fc(sum(bool(E[k]["met"]) for k in ("E8_1", "E8_2", "E8_3", "E8_4"))))
    if (S / "U.json").exists():
        U = json.load(open(S / "U.json")); mac("su_n", fi(U["n_jobs"])); mac("su_tp", fi(U["tp"])); mac("su_fn", fi(U["fn"])); mac("su_fp", fi(U["fp"])); mac("su_tn", fi(U["tn"])); mac("su_sens", fp(U["sensitivity"])); mac("su_spec", fp(U["specificity"], 1)); mac("su_verdict", pm(U["criterion_met"])); mac("su_unusable_jobs", fi(U["tp"] + U["fn"])); mac("su_usable_jobs", fi(U["fp"] + U["tn"]))
        mac("su_unusable_n", fc(len(U["unusable_instances"]))); mac("su_unusable", ", ".join("\\texttt{" + k.replace("_", "\\_") + "}" for k in U["unusable_instances"])); import collections; fa = collections.Counter(x["instance"] for x in U["false_alarms"]); mac("su_fp_inst", ", ".join(f"\\texttt{{{k.replace(chr(95), chr(92) + chr(95))}}} ({fc(v)})" for k, v in sorted(fa.items()))); mac("su_fp_all_n64", "yes" if all(x["N"] == 64 for x in U["false_alarms"]) else "no")

    rn = S / "runs_needed_check.json"
    if rn.exists():
        Rn = json.load(open(rn)); k = "pod_gp[rbf,r=32]"; mac("se_rn_start", fp(Rn[f"{k}@256"], 2)); mac("se_rn_mid", fp(Rn[f"{k}@320"], 2)); mac("se_rn_end", fp(Rn[f"{k}@512"], 2))
    if (S / "U.json").exists():
        U = json.load(open(S / "U.json")); cv = [x["best_cv"] for x in U["false_alarms"]]; ts = [x["test_sel"] for x in U["false_alarms"]]; mac("su_fp_cv_min", fd(min(cv), 2)); mac("su_fp_cv_max", fd(max(cv), 2)); mac("su_fp_test_min", fd(min(ts), 2)); mac("su_fp_test_max", fd(max(ts), 2))
