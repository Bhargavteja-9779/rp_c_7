"""Automated check: for each experiment, the commit that pre-registered it precedes the first commit that contains its raw results.
Limitation: commit time of raw files is >= the time the runs finished; the check shows protocol-before-results-in-history, not protocol-before-first-run (supported separately by the run chain logs)."""
import subprocess, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sh = lambda *a: subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout.strip()
PRE = {"A": "bcf7f30", "D": "bcf7f30", "B": "bcf7f30", "A2": "72cb02c", "E": "72cb02c", "A3": "c9a7b93", "G": "c9a7b93", "F": "c9a7b93", "H8": "48a0698", "H32": "48a0698", "G3": "4cd411a"}
rows = []
for k, c in PRE.items():
    t_pre = int(sh("git", "show", "-s", "--format=%ct", c)); first = sh("git", "log", "--diff-filter=A", "--format=%h %ct", "--", f"results/raw_exp{k}").splitlines()
    if not first: rows.append(dict(exp=k, prereg_commit=c, ok=None, note="no raw results in history")); continue
    h, t_res = first[-1].split(); t_res = int(t_res)
    rows.append(dict(exp=k, prereg_commit=c, first_results_commit=h, hours_prereg_before_first_results_commit=round((t_res - t_pre) / 3600, 2), ok=bool(t_res >= t_pre)))
(ROOT / "audit/prereg_order_check.json").write_text(json.dumps(rows, indent=1)); [print(r) for r in rows]
