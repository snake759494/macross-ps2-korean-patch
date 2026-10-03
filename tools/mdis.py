import sys,json;sys.path.insert(0,'tools');from elf import *
S=json.load(open('work/syms.json'));A={}
for k,v in S.items():
    if v[0]: A.setdefault(v[0],k)
def p(name):
    a,n=S[name] if name in S else (int(name,16),400)
    print('=====',name)
    for k in range(n//4):
        m,o=dis1(a+4*k);t=''
        if m in('jal','j'):
            try:t=A.get(int(o,16),'')
            except:pass
        print('%08x: %s %s %s'%(a+4*k,m,o,t))
for n in sys.argv[1:]: p(n)
