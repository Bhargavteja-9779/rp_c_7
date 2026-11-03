#!/bin/bash
# Relaunch the Stage 6 chain if the container restarted and it is not finished (resumable).
cd "$(dirname "$0")"
if grep -q CHAIN6_FINISHED ../results/chain6_stdout.log 2>/dev/null; then echo finished; elif pgrep -f run_chain6 >/dev/null; then echo running; else (nohup ./run_chain6.sh >/dev/null 2>&1 &); echo relaunched; fi
