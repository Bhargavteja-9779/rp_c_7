"""Part 5 of aggregate.py: Stage 9 (results/s9; protocol_addendum_v3.4.md): calibrated budget forecast. Macros prefix 'sf'."""
import json


def part5(ag):
    R, mac, fi, fc, fd, fp = ag.R, ag.mac, ag.fi, ag.fc, ag.fd, ag.fp; S = R / "s9"; pm = lambda m: "met" if m else "not met"
    if not (S / "heldout.json").exists(): return
    L, H, X = (json.load(open(S / f)) for f in ("lofo.json", "heldout.json", "posthoc.json")); m, hm, c = L["metrics"], H["metrics"], H["criteria"]
    mac("sf_dev_cases", fi(L["n_cases"])); mac("sf_dev_problems", fi(L["n_problems"])); mac("sf_dev_families", fi(L["n_families"])); mac("sf_held_cases", fi(H["n_cases"])); mac("sf_held_problems", fi(H["n_problems"])); mac("sf_all_cases", fi(L["n_cases"] + H["n_cases"]))
    mac("sf_zero_dev_share", fp(m["F0"]["share2"])); mac("sf_zero_held_share", fp(hm["F0"]["share2"])); mac("sf_zero_all_share", fp(X["raw_forecast_share2"]["all"])); mac("sf_zero_dev_med", fd(10 ** m["F0"]["med_abs"], 2)); mac("sf_zero_held_med", fd(10 ** hm["F0"]["med_abs"], 2))
    mac("sf_zero_bias_dev", fd(X["raw_forecast_bias_decades"]["dev"], 2)); mac("sf_zero_bias_held", fd(X["raw_forecast_bias_decades"]["held"], 2))
    q = X["raw_forecast_factor_quantiles"]; mac("sf_q_half", fd(q["q50"], 1)); mac("sf_q_eighty", fd(q["q80"], 1)); mac("sf_q_ninety", fd(q["q90"], 0))
    for k, nm in (("F2", "two"), ("F3", "three"), ("F4", "four"), ("F5", "five")): mac(f"sf_{nm}_dev_share", fp(m[k]["share2"])); mac(f"sf_{nm}_held_share", fp(hm[k]["share2"]))
    mac("sf_three_dev_cov", fp(m["F3"]["cov80"])); mac("sf_three_dev_width", fd(m["F3"]["width80"], 2)); mac("sf_two_dev_width", fd(m["F2"]["width80"], 2)); mac("sf_two_held_cov", fp(hm["F2"]["cov80"])); mac("sf_four_held_cov", fp(hm["F4"]["cov80"]))
    k1, k2, k3, k4, k5 = c["K1"], c["K2"], c["K3"], c["K4"], c["K5"]
    mac("sf_kone_cov", fp(k1["cov80"])); mac("sf_kone_lo", fp(k1["cov80_ci"][0])); mac("sf_kone_hi", fp(k1["cov80_ci"][1])); mac("sf_kone_verdict", pm(k1["met"]))
    mac("sf_ktwo_ratio", fd(k2["med_ratio"], 2)); mac("sf_ktwo_gain", fd(abs(100 * k2["share_gain"]), 0)); mac("sf_ktwo_verdict", pm(k2["met"])); mac("sf_kthree_verdict", pm(k3["met"])); mac("sf_kfour_width", fd(k4["width80"], 2)); mac("sf_kfour_verdict", pm(k4["met"]))
    for key, nm in (("one_pct", "one"), ("tenth_pct", "tenth")): t = k5[key]; mac(f"sf_kfive_{nm}_n", fi(t["n_confident"])); mac(f"sf_kfive_{nm}_share", fp(t["share_reached"])); mac(f"sf_kfive_{nm}_verdict", pm(t["met"]))
    mac("sf_met_count", fc(sum(bool(x) for x in (k1["met"], k2["met"], k3["met"], k4["met"], k5["one_pct"]["met"] and k5["tenth_pct"]["met"]))))
    d, hc, fq = X["development_lofo"], X["heldout"], X["frozen_q"]
    mac("sf_ph_dev_cov_eighty", fp(d["cov80"])); mac("sf_ph_dev_cov_ninety", fp(d["cov90"])); mac("sf_ph_held_cov_eighty", fp(hc["cov80"])); mac("sf_ph_held_cov_ninety", fp(hc["cov90"])); mac("sf_ph_held_lo", fp(hc["cov80_ci_problem_level"][0])); mac("sf_ph_held_hi", fp(hc["cov80_ci_problem_level"][1]))
    mac("sf_ph_w_eighty", fd(fq["width80_decades"], 1)); mac("sf_ph_w_ninety", fd(fq["width90_decades"], 1)); mac("sf_ph_f_eighty", fd(10 ** fq["q80"], 1)); mac("sf_ph_f_ninety", fd(10 ** fq["q90"], 0))
    for n0, nm in ((64, "sixtyfour"), (128, "onetwentyeight"), (256, "twofiftysix")): mac(f"sf_ph_q_eighty_{nm}", fd(X["by_N0"][str(n0)]["q80_factor"], 1)); mac(f"sf_ph_share_{nm}", fp(X["by_N0"][str(n0)]["share2"]))
    for key, nm in (("one_pct", "one"), ("tenth_pct", "tenth")):
        t = X["decision_heldout"][key]; mac(f"sf_dec_{nm}_prec", fp(t["precision"])); mac(f"sf_dec_{nm}_rec", fp(t["recall"])); mac(f"sf_dec_{nm}_pprec", fp(t["point_rule_precision"])); mac(f"sf_dec_{nm}_prec_rec", fp(t["point_rule_recall"]))
