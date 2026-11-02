#!/bin/bash
# Stage 6 chain: T (legacy five methods), C (SurroSelect), S (strong tuned NN). Resumable (atomic per-job JSON).
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"
python3 run_v2.py --exp 6T --workers 4 >> ../results/chain6_stdout.log 2>&1
echo T_FINISHED >> ../results/chain6_stdout.log
python3 experiments/exp_s6.py --exp C --workers 4 >> ../results/chain6_stdout.log 2>&1
echo C_FINISHED >> ../results/chain6_stdout.log
python3 experiments/exp_s6.py --exp S --workers 4 >> ../results/chain6_stdout.log 2>&1
echo CHAIN6_FINISHED >> ../results/chain6_stdout.log
