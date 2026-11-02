import sys; sys.path.insert(0,'.')
import build_comp as C, cv2, numpy as np
S=C.S
key=sys.argv[1]; cands=[int(x) for x in sys.argv[2].split(',')]
k,i=key.split('/'); s1=cv2.imread(f'{S}/slides/out/درس{k}/{i}.png')
ink=np.abs(s1.astype(np.int16)-C.PL1.astype(np.int16)).max(2)>22; ink[:440]=False; ink[1015:]=False
n,lab,st,_=cv2.connectedComponentsWithStats(cv2.dilate(ink.astype(np.uint8),np.ones((5,5),np.uint8)))
comps=sorted([j for j in range(1,n)], key=lambda j:-st[j,4])[:8]
for j in comps:
    x,y,w,h,a=st[j]
    if w<60: continue
    crop=C.gray(s1[y-3:y+h+3,x-3:x+w+3]); best=None
    for pg in cands:
        im=C.page1c(pg)
        for s in np.arange(0.5,1.001,0.01):
            P=C.gray(cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_AREA))
            if P.shape[0]<crop.shape[0] or P.shape[1]<crop.shape[1]: continue
            m=cv2.matchTemplate(P,crop,cv2.TM_CCOEFF_NORMED); _,mx,_,loc=cv2.minMaxLoc(m)
            if best is None or mx>best[0]: best=(round(float(mx),3),pg,round(float(s),3),loc)
    print(key,(x,y,w,h),best,flush=True)
