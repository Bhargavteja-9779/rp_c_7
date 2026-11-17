#!/bin/bash
# Stage 10 chain (protocol_addendum_v3.5.md). Resumable.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"; L=../results/chain10_stdout.log
python3 experiments/exp_s10.py --exp F --workers 4 >> $L 2>&1; echo F_FINISHED >> $L
python3 experiments/exp_s10.py --exp S --workers 4 >> $L 2>&1; echo S_FINISHED >> $L
python3 experiments/exp_s10.py --exp H --workers 4 >> $L 2>&1; echo CHAIN10_FINISHED >> $L
