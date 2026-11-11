import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt, pickle
S=bt.S
b33=1674.0; b31=bt.line_base(31,1420,1600)
A=bt.P(33,2415,3190,1580,1760,b33,ah=83)                   # لأن إيصال الماء إلى
asul=bt.scaled(bt.P(31,1190,1470,1400,1600,b31,down=0.4),83/98)     # أصول (من ص31)
shaar=bt.scaled(bt.P(31,912,1162,1400,1600,b31,down=0.4),83/98)               # الشعر (من السطر نفسه)
C=bt.P(33,650,1600,1580,1760,b33,ah=83)                    # والبشرة واجب في الغسل
e5=bt.assemble([A,asul,shaar,C],[30,30,30])
old=bt.P(33,650,3190,1580,1760,b33,ah=83)
bt.preview([old,e5],S+'/txt/e5.png',sc=0.6)
pickle.dump(dict(e5=e5),open(S+'/txt/e5.pkl','wb')); print(b31, e5[0].shape)
