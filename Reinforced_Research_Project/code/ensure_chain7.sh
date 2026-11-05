#!/bin/bash
# Relaunch the Stage 7 chain after a container restart if it is not finished (resumable).
cd "$(dirname "$0")"; chmod +x run_chain7.sh
if grep -q CHAIN7_FINISHED ../results/chain7_stdout.log 2>/dev/null; then echo finished; elif pgrep -f run_chain7 >/dev/null; then echo running; else (nohup ./run_chain7.sh >/dev/null 2>&1 &); echo relaunched; fi
