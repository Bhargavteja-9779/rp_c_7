#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"
python3 run_v2.py --exp H8 --workers 4 >> ../results/chain4_stdout.log 2>&1
python3 run_v2.py --exp H32 --workers 4 >> ../results/chain4_stdout.log 2>&1
echo CHAIN4_FINISHED >> ../results/chain4_stdout.log
