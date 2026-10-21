#!/bin/bash
# Runs the three v2 experiments sequentially (each is resumable). OMP/MKL/OPENBLAS threads pinned to 1.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"
python3 run_v2.py --exp A --workers 4 >> ../results/chain_stdout.log 2>&1
python3 run_v2.py --exp D --workers 4 >> ../results/chain_stdout.log 2>&1
python3 experiments/exp_b_strong_nn.py >> ../results/chain_stdout.log 2>&1
echo CHAIN_FINISHED >> ../results/chain_stdout.log
