#!/bin/bash
cd /tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/v4k
cat jobs_fix.txt | xargs -P 3 -L 1 bash -c 'python3 compose.py $0 $1 $2 $3 $4 > $4.log 2>&1; echo "finished $4 $(tail -1 $4.log)" >> progress_fix.log'
python3 rebuild.py > rebuild.log 2>&1
python3 assemble4k.py 1 2 3 4 > assemble.log 2>&1
echo AFTERDONE >> progress_fix.log
