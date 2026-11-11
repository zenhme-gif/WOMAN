import cv2, numpy as np, subprocess, json, sys, os
S='/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
out={}
for n in range(1,144):
    P=cv2.imread(f'{S}/hr/pages4k/{n:03d}.png')
    if P is None: continue
    f=P.astype(int); top=f[300:820]
    red=(top[...,2]-top[...,1]>60)&(top[...,2]-top[...,0]>60)
    if red.sum()<20000: continue
    ys,xs=np.nonzero(red); y0,y1,x0,x1=ys.min()+300,ys.max()+300,xs.min(),xs.max()
    reg=P[y0:y1,x0:x1]; g=reg.min(2)
    txt=(g>170).astype(np.uint8)*255  # white text
    im=255-txt
    p=f'{S}/ocr/ban/{n:03d}.png'; cv2.imwrite(p,im)
    r=subprocess.run(['tesseract',p,'-','-l','ara','--psm','6','tsv'],capture_output=True,text=True).stdout
    ws=[]
    for l in r.splitlines()[1:]:
        c=l.split('\t')
        if len(c)==12 and c[11].strip() and float(c[10])>0:
            ws.append(dict(t=c[11],x=int(c[6])+int(x0),y=int(c[7])+int(y0),w=int(c[8]),h=int(c[9]),conf=float(c[10])))
    out[n]=ws
json.dump(out,open(f'{S}/ocr/banners.json','w'),ensure_ascii=False)
for n,ws in out.items(): print(n,' '.join(w['t'] for w in ws))
