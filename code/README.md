# surrogate_bench — pre-registered comparison of linear-subspace vs nonlinear-output surrogates for parametric PDEs

Everything reported in `manuscript/Final_Manuscript.*` is produced by this code. All data are **synthetic** (numpy/scipy PDE solvers).

## Reproduce
```bash
pip install -r requirements.txt
python -m pytest -q tests                      # 27 tests (solvers vs exact/refinement checks, methods, leakage, statistics)
python run_all.py --mode quick                 # pipeline check ONLY (2 instances, B=2, 40 epochs) -> results/quick_NOT_EVIDENCE/ (not evidence)
python run_all.py --mode full --workers 4      # pre-registered experiment: 16 instances x 6 N x 3 seeds x 5 methods (~3.5 h on 4 cores) + analysis
python run_all.py --mode full --stage analysis # analysis only (needs results/raw/*.json; regenerates statistics.json, tables/)
python experiments/exploratory.py e1|e23|e4    # post-hoc exploratory analyses (see research_design/deviations.md)
python -c "import sys; sys.path.insert(0,'src'); from surrogate_bench import figures; figures.make_all('../results')"
python ../manuscript/build_manuscript.py && (cd ../manuscript && pandoc Final_Manuscript.md -o Final_Manuscript.docx --resource-path=.:.. && python postprocess_docx.py Final_Manuscript.docx)
python ../review/check_claims.py               # automated claim-to-evidence checks
```
Set `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1` before launching the full run (otherwise BLAS threads oversubscribe the cores).
The full run is resumable (a job's JSON is written atomically only when complete).

## Layout
`src/surrogate_bench/`: `problems.py` (16 PDE instances + dev problem), `data.py` (pools, caching), `methods.py` (5 surrogates), `hpo.py` (matched random search), `diagnostics.py` (pilot features), `stats.py`, `analysis.py`, `figures.py`, `experiment.py`. `configs/protocol.json`: frozen settings. `tests/`: unit/integration tests.

## Implementation notes not in the paper
* POD+MLP trains on POD coefficients divided by sigma_1/sqrt(N); direct/bottleneck MLPs train on (field - mean)/std.
* Mini-batching: full batch if N <= 512, else 512. Adam, cosine LR, 1500 epochs, float32, one CPU thread.
* POD+GP: ARD kernel hyper-parameters optimised for the leading 4 modes on <=300 random points (single start); remaining modes reuse the 4th kernel. Known failure: 4/288 final fits > 3x worse than the selected trial (see manuscript E5).
* Data cache `data_cache/` (~180 MB) is regenerated deterministically (seeded by instance name) and is not committed.

## Limitations of reproducibility
Bit-identical reproduction of neural-network results across different CPUs/BLAS builds is not guaranteed; GP/polynomial results and all statistics are deterministic given the raw JSON. The first full run was independent of any fixed hardware beyond a 4-core CPU container. Fresh-clone audit: see `review/final_audit.md`.
