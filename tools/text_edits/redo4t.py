"""الدرس الرابع: وصل إطارات «موضوعات الدرس» المرقّعة (نص المربع الأول الجديد) في النسخة الحالية lesson04_new."""
import sys, os, shutil
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/splice')
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import splice as SP, l4t_patch as LP
S = LP.S
N0, N1 = 536, 806
base = f'{S}/splice/lesson04_new_prev.mp4'
if not os.path.exists(base): shutil.copy(f'{S}/splice/lesson04_new.mp4', base)
P = LP.Patcher()
SP.run(base, [(N0 / 30, N1 / 30, P.get)], f'{S}/splice/lesson04_new.mp4', f'{S}/splice/w4t')
import json; json.dump([list(map(str, l)) for l in P.log], open(f'{S}/splice/redo4t_log.json', 'w'))
print('patched frames', len(P.log))
