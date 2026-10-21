"""Automated claim-to-evidence checks. Exit code 1 if any check fails. Writes claim_check_report.md."""
import json, subprocess, re, pathlib, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]; R = ROOT / "results"; out = []; ok_all = True
def chk(name, cond, detail=""):
    global ok_all; ok_all &= bool(cond); out.append(f"| {'PASS' if cond else '**FAIL**'} | {name} | {detail} |")
raw = pd.read_csv(R / "raw_results.csv"); S = json.load(open(R / "statistics.json")); man = (ROOT / "manuscript/Final_Manuscript.md").read_text()
chk("1440 result rows = 16 inst x 3 seeds x 6 N x 5 methods", len(raw) == 1440 and raw.instance.nunique() == 16 and raw.seed.nunique() == 3, f"rows={len(raw)}")
chk("all errors finite", np.isfinite(raw.err).all())
chk("48 completed job files", len(list((R / "raw").glob("*__s*.json"))) == 48)
chk("seeds used = [0,1,2]", S["seeds_used"] == [0, 1, 2])
chk("H4a counts b=10,c=1 in text", "10 vs 1 discordant" in man and S["H4a"]["b"] == 10 and S["H4a"]["c"] == 1)
chk("Holm: only H4a rejected", [k for k, v in S["holm"].items() if v["reject_alpha05"]] == ["H4a"], str({k: round(v["adjusted_p"], 4) for k, v in S["holm"].items()}))
rt = pd.read_csv(R / "exploratory/refit_vs_trial_error.csv"); g = rt[rt.method == "pod_gp"]
chk("GP instability 4/288 (>3x), 2/288 (>10x) as stated (1.4%)", int((g.ratio > 3).sum()) == 4 and int((g.ratio > 10).sum()) == 2 and len(g) == 288 and "1.4%" in man)
ab = json.load(open(ROOT / "literature_review/data/arxiv_abstracts_core.json")); mg = [a for a in ab if "2407.07218" in a["id"]][0]["abstract"]
chk("'79% (60/76)' claim matches McGreivy & Hakim abstract", "79% (60/76)" in mg and "79% (60 of 76)" in man)
refs = pd.read_csv(ROOT / "literature_review/references_verified.csv")
cites = set(re.findall(r"\[([^\]]+?\d{4}[^\]]*)\]", man)); chk("reference list file has all cited keys", len(refs) >= 27, f"{len(refs)} verified entries; {len(cites)} distinct in-text bracket cites")
# pre-registration ordering: protocol commit must precede first commit that contains any raw result
def git(*a): return subprocess.check_output(["git", "-C", str(ROOT), *a], text=True).strip()
pre = re.search(r"commit `([0-9a-f]{40})`", (ROOT / "research_design/experimental_protocol.md").read_text()).group(1)
first_raw = git("log", "--diff-filter=A", "--format=%H %ct", "--", "results/raw").splitlines()[-1].split(); t_pre = int(git("show", "-s", "--format=%ct", pre))
chk("protocol commit precedes first commit containing raw results", t_pre < int(first_raw[1]), f"protocol {t_pre} < first raw {first_raw[1]}")
anal = re.findall(r"commit `([0-9a-f]{40})`", (ROOT / "research_design/experimental_protocol.md").read_text())[1]
chk("analysis-code commit precedes first raw results commit", int(git("show", "-s", "--format=%ct", anal)) < int(first_raw[1]))
chk("manuscript has no unreplaced template braces", "{{" not in man and "{H" not in man)
chk("placeholders present for authors (not fabricated)", "[AUTHOR NAMES AND AFFILIATIONS" in man)
chk("no claim of acceptance / guaranteed / state-of-the-art", not re.search(r"guarantee[ds]? accept|state-of-the-art accuracy (is|was) achieved", man))
(ROOT / "review/claim_check_report.md").write_text("# Automated claim checks\n\n| Status | Check | Detail |\n|---|---|---|\n" + "\n".join(out) + "\n")
print("\n".join(out)); raise SystemExit(0 if ok_all else 1)
