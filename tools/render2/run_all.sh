#!/bin/bash
S=/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad; cd $S/r2
# الجزء أ: إطارات الفيديو القديم من الإطار المفتاحي 227.833 إلى بداية الانتقال 232.867 (151 إطاراً)، مُعاد ترميزها كما هي
ffmpeg -loglevel error -y -ss 227.8333 -i $S/work/lesson2_cur.mp4 -map 0:v -frames:v 151 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -video_track_timescale 15360 pA.mp4
python3 render_chunk.py 232.86667 527.0 c1.mp4 base > c1.log 2>&1 &
python3 render_chunk.py 527.0 793.0 c2.mp4 > c2.log 2>&1 &
python3 render_chunk.py 793.0 1063.4 c3.mp4 > c3.log 2>&1 &
wait
for f in pA c1 c2 c3; do echo "$f $(ffmpeg -hide_banner -i $f.mp4 2>&1 | grep -o 'Duration: [0-9:.]*')"; done
