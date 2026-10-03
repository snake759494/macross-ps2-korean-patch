import sys,os,json,glob,struct,re
sys.path.insert(0,'tools')
import cricmp,bootdat,textenc,font,isobuild,cvm
SRC='Chou Jikuu Yousai Macross (Japan).iso'
DST='Chou Jikuu Yousai Macross (Japan) (Korean).iso'
def load_tr():
    tr={}
    for f in sorted(glob.glob('translation/batch/*.json'))+sorted(glob.glob('translation/extra/*.json')):
        for x in json.load(open(f,encoding='utf8')):
            if x.get('ko'): tr[x['jp']]=x['ko']
    return tr
def build_bootdat(tr,bad):
    d=cricmp.decompress(open('work/ext/JPN/BOOTDAT.CMP','rb').read())
    # ids/prefixes are re-extracted from the user's own BOOTDAT; only Korean text is stored in the repo
    items=[]
    for ti,t in enumerate(bootdat.tables(d)):
        for si,raw in enumerate(t):
            s0=raw.decode('cp932','replace');pre=''
            if ti<=4 and len(s0)>=6 and all(c in '0123456789 ' for c in s0[:6]): pre=s0[:6]
            if ti==0 and len(s0)>=14 and s0[6:14].isdigit(): pre=s0[:14]
            items.append(dict(id=f'{ti}_{si}',pre=pre))
    KO=json.load(open('translation/strings_ko.json',encoding='utf8'))
    T=bootdat.tables(d);new=[list(t) for t in T];n=0
    for it in items:
        ti,si=map(int,it['id'].split('_'))
        ko=KO.get(it['id'])
        if ko is None: continue
        voiced=ti in (1,3) and len(it['pre'])>=6 and it['pre'][3:6].isdigit()
        W=270 if voiced else {0:480,1:480,2:480,3:480,4:520}.get(ti)
        if W: ko=textenc.wrap(ko,W)
        pre=it['pre']
        if voiced and pre[2]=='0': pre=pre[:2]+'1'+pre[3:]   # enable subtitle window for voiced radio lines
        new[ti][si]=pre.encode('ascii')+textenc.enc(ko,bad);n+=1
    print('bootdat strings translated',n,'/',len(items))
    return bootdat.rebuild(d,new)
def build_elf(bad):
    d=bytearray(open('work/SLPM_654.05','rb').read())
    for x in json.load(open('translation/elf_ko.json',encoding='utf8')):
        b=textenc.enc(x['ko'],bad)
        assert len(b)<=x['cap'],(x['jp'],len(b),x['cap'])
        o=x['off'];d[o:o+x['cap']+1]=b+bytes(x['cap']+1-len(b))
    os.makedirs('work/out',exist_ok=True);open('work/out/SLPM_654.05','wb').write(d)
def main():
    tr=load_tr();bad=set()
    build_elf(bad)
    extra={}
    for f in glob.glob('work/patched/*.py'): pass
    boot=build_bootdat(tr,bad)
    if bad: print('UNENCODABLE',''.join(sorted(bad)))
    # texture-patched files (must run before font so CRSDAT atlas edits are kept)
    import subprocess;subprocess.run([sys.executable,'-X','utf8','tools/texapply.py'],check=True)
    crs_src='work/texout/ext/JPN/CRSDAT.MRG' if os.path.exists('work/texout/ext/JPN/CRSDAT.MRG') else 'work/ext/JPN/CRSDAT.MRG'
    crs=font.build(open(crs_src,'rb').read(),fontpath='NanumSquareNeo-dEb.ttf')
    jpn={'BOOTDAT.CMP':cricmp.compress(boot)}
    tex={}
    for f in glob.glob('work/texout/**/*',recursive=True):
        if os.path.isdir(f): continue
        rel=f.replace(os.sep,'/').split('work/texout/')[1];kind,cv,name=rel.split('/')
        data=open(f,'rb').read()
        if kind=='dec': name=name[:-4]+'.CMP';data=cricmp.compress(data)
        tex.setdefault(cv,{})[name]=data
    jpn.update(tex.get('JPN',{}));jpn['CRSDAT.MRG']=crs
    # optional extra patched files from texture/other steps
    for f in glob.glob('work/out/JPN/*'): jpn[os.path.basename(f)]=open(f,'rb').read()
    binf={os.path.basename(f):open(f,'rb').read() for f in glob.glob('work/out/BIN/*')};binf.update(tex.get('BIN',{}))
    movf={os.path.basename(f):open(f,'rb').read() for f in glob.glob('work/out/MOV/*')}
    root={'CRSDAT.MRG':crs}
    if os.path.exists('work/out/SLPM_654.05'): root['SLPM_654.05']=open('work/out/SLPM_654.05','rb').read()
    isobuild.build(SRC,DST,{'JPN':jpn,'BIN':binf,'MOV':movf},root)
    print('built',DST)
if __name__=='__main__': main()
