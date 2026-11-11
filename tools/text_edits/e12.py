import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt, numpy as np, pickle
S=bt.S
B=dict(p9=1547.0, p12=1547.0, p57=1883.0, p74=1547.0, p24=1715.0, p14=1884.0)
# E1: p10 السطر الثاني «شعرها فلا يلزمها أن تعود» (ارتفاع الألف 76)
p10l2=1652
shaarha=bt.P(10,1955,2195,1540,1730,p10l2,ah=76)
fala=bt.P(10,1825,1942,1540,1730,p10l2,ah=76)
taud=bt.P(10,1640,1815,1540,1730,p10l2,ah=76)
yalz=bt.scaled(bt.P(12,1420,1570,1420,1620,B['p12'],cxa=1445),76/98)
maha=bt.scaled(bt.P(57,2895,3058,1760,1950,B['p57'],cxb=3040),76/97)
an=bt.scaled(bt.P(9,595,725,1420,1600,B['p9']),76/98)
e1=bt.assemble([shaarha,fala,bt.assemble([yalz,maha],[4]),an,taud],[30,30,30,30])
old1=bt.P(10,1640,2195,1540,1730,p10l2,ah=76)
# E2: p14 «لأثر» بدل «لحديث» (ارتفاع الألف 97)
la=bt.P(24,3075,3190,1580,1760,B['p24'],cxa=3085)
thr=bt.P(74,1140,1245,1410,1600,B['p74'],cxa=1150,cxb=1240)
lathar=bt.assemble([la,thr],[6])
lihadith=bt.P(14,2785,3150,1760,1950,B['p14'])
bt.preview([old1,e1,lihadith,lathar],S+'/txt/e12.png')
import cv2
ym=bt.assemble([yalz,maha],[4]); a=ym[0]; cv2.imwrite(S+'/txt/ylz.png', cv2.resize((255-a*255).astype('uint8'),None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST))
pickle.dump(dict(e1=e1,lathar=lathar),open(S+'/txt/e12.pkl','wb'))
print(e1[0].shape, lathar[0].shape)
