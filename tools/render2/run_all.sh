#!/bin/bash
S=/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad; cd $S/r2
python3 render_chunk.py 261.16667 527.0 c1.mp4 base > c1.log 2>&1 &
python3 render_chunk.py 527.0 793.0 c2.mp4 > c2.log 2>&1 &
python3 render_chunk.py 793.0 1063.4 c3.mp4 > c3.log 2>&1 &
wait
tail -1 c1.log c2.log c3.log
