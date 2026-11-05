#!/bin/bash
# Stage 7 chain (protocol_addendum_v3.2.md). Resumable (atomic per-job JSON); each step is skipped if its output exists.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"; L=../results/chain7_stdout.log
python3 experiments/exp_s7.py --exp E7gen >> $L 2>&1; echo E7GEN_FINISHED >> $L
python3 run_v2.py --exp 7T --workers 4 >> $L 2>&1; echo T7_FINISHED >> $L
python3 experiments/exp_s7.py --exp C7 --workers 4 >> $L 2>&1; echo C7_FINISHED >> $L
python3 experiments/exp_s7.py --exp S7 --workers 4 >> $L 2>&1; echo S7_FINISHED >> $L
python3 experiments/exp_s7.py --exp N7 --workers 4 >> $L 2>&1; echo N7_FINISHED >> $L
python3 experiments/exp_s7.py --exp SP --workers 4 >> $L 2>&1; echo SP_FINISHED >> $L
python3 experiments/exp_s7.py --exp E7 >> $L 2>&1; echo CHAIN7_FINISHED >> $L
