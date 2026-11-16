#!/bin/bash
# Stage 9 chain (protocol_addendum_v3.4.md): learning-curve dataset. Resumable.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"; L=../results/chain9_stdout.log
python3 experiments/exp_s9.py --workers 4 >> $L 2>&1; echo CHAIN9_FINISHED >> $L
