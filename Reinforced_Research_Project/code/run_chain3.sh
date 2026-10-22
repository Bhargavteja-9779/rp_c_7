#!/bin/bash
# Waits for chain 2 (A2, E) then runs A3, G, F.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"
while ! grep -q CHAIN2_FINISHED ../results/chain2_stdout.log 2>/dev/null; do sleep 30; done
python3 run_v2.py --exp A3 --workers 4 >> ../results/chain3_stdout.log 2>&1
python3 run_v2.py --exp G --workers 4 >> ../results/chain3_stdout.log 2>&1
python3 experiments/exp_f_precision.py >> ../results/chain3_stdout.log 2>&1
echo CHAIN3_FINISHED >> ../results/chain3_stdout.log
