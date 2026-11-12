#!/bin/bash
# Stage 8 chain (protocol_addendum_v3.3.md). Resumable.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"; L=../results/chain8_stdout.log
python3 experiments/exp_s8.py --exp gen >> $L 2>&1; echo E8GEN_FINISHED >> $L
python3 experiments/exp_s8.py --exp run >> $L 2>&1; echo CHAIN8_FINISHED >> $L
