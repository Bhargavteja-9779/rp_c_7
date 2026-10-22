# Independent verification of v2 results (no shared analysis code)

| Status | Check | Detail |
|---|---|---|
| PASS | Exp A: 24 jobs = 8 instances x 3 seeds |  |
| PASS | Exp A: 720 records, 8 trials each, argmin-val config recorded, recorded error = mean of per-sample errors | records=720 |
| PASS | Exp A: every NN record has a logged loss curve (new in v2) | missing=0 |
| PASS | P1 recomputed (rho, exact permutation p) equals reported | rho=-0.3810 p=0.1799 |
| PASS | P2 mean squared-error gain and RMSEs recomputed | gain=0.5983 |
| PASS | S1 recomputed (6 of 10 non-tie cells correct) | 6/10 |
| PASS | frozen rules cite the v1 source commit 931b306 |  |
| PASS | Exp D: 72 jobs, 432 records (24 inst x 3 seeds x 6 N x 1 method), all pod_krr with 8 trials | jobs=72 records=432 |
