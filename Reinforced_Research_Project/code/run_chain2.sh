#!/bin/bash
# Waits for chain 1 (A, D, B) to finish, then runs A2 and E.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"
while ! grep -q CHAIN_FINISHED ../results/chain_stdout.log 2>/dev/null; do sleep 30; done
python3 run_v2.py --exp A2 --workers 4 >> ../results/chain2_stdout.log 2>&1
python3 run_v2.py --exp E --workers 4 >> ../results/chain2_stdout.log 2>&1
echo CHAIN2_FINISHED >> ../results/chain2_stdout.log
