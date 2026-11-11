import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt, edit, pickle, cv2, numpy as np
S=bt.S
d=pickle.load(open(S+'/txt/e12.pkl','rb')); d5=pickle.load(open(S+'/txt/e5.pkl','rb'))
# E2 ص14
rest=bt.P(14,600,2770,1760,1960,1884.0)
line=bt.assemble([d['lathar'],rest],[43])
img,info=edit.replace_line(14,1884.0,97,line); edit.save(14,img); print('p14',info)
# E1 ص10 السطر الثاني (خط القاعدة 1652، الألف 76)
img,info=edit.replace_line(10,1652.0,76,d['e1'],up=1.0,down=0.55,center=1918.5,x0=1600,x1=2250); edit.save(10,img); print('p10',info)
# E5 ص33 السطر الثاني (خط القاعدة 1674، الألف 83)
img,info=edit.replace_line(33,1674.0,83,d5['e5']); edit.save(33,img); print('p33',info)
a=cv2.imread(S+'/hr/pages4k_edit/014.png'); b=cv2.imread(S+'/hr/pages4k_edit/010.png'); c=cv2.imread(S+'/hr/pages4k_edit/033.png')
cv2.imwrite(S+'/txt/edited3.png', np.vstack([cv2.resize(a[1350:2100,500:3340],None,fx=0.33,fy=0.33), cv2.resize(b[1380:2080,500:3340],None,fx=0.33,fy=0.33), cv2.resize(c[1350:1800,500:3340],None,fx=0.33,fy=0.33)]))
