# Independent recomputation of key results (no shared analysis code)

| Status | Check | Detail |
|---|---|---|
| PASS | 48 job files, 16 instances x 3 seeds |  |
| PASS | 1440 records; each has 8 trials numbered 0..7 | records=1440, bad=0 |
| PASS | val_best == min trial validation error in every record | mismatches=0 |
| PASS | best_cfg == config of the min-validation trial | mismatches=0 |
| PASS | recorded test_err == mean of per-sample errors in .npz (float32 tol 1e-4) | mismatches=0 |
| PASS | H1a recomputed (median, p) equals statistics.json | median=-0.0592 p=0.8739 |
| PASS | H1b recomputed (k of 16) equals statistics.json | k=5 |
| PASS | H4a discordant counts recomputed (b, c) equal statistics.json | b=10 c=1 |
| PASS | H4a McNemar p recomputed |  |
| PASS | H2 LOFO RMSEs recomputed equal statistics.json (B0,B1,M_spec) | 1.123 4.172 0.924 |
| PASS | pilot feature log_cv_err_r4 recomputed from data cache (2 instances, seed 1) |  |
