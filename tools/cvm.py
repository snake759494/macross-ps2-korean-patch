"""CRI CVM (ROFS) reader. ISO9660 image located at +0x1800 inside the CVM."""
import struct
ISO='Chou Jikuu Yousai Macross (Japan).iso'
CVMS={'JPN':(343003,23187456),'BIN':(225957,239710208),'ETC':(503783,199122944),'MOV':(354325,306089984),'ADXJ':(3416,455763968)}
BASE=0x1800
def read_dir(f,cvm_off,lba,size,path=''):
    f.seek(cvm_off+BASE+lba*2048);d=f.read(size);out=[]
    i=0
    while i<len(d):
        l=d[i]
        if l==0:
            i=(i//2048+1)*2048;continue
        r=d[i:i+l]
        elba=struct.unpack_from('<I',r,2)[0];esz=struct.unpack_from('<I',r,10)[0];flags=r[25]
        nl=r[32];name=r[33:33+nl]
        if name not in (b'\0',b'\1'):
            n=name.decode('ascii','replace').split(';')[0]
            rec_off=cvm_off+BASE+lba*2048+i
            if flags&2: out+=read_dir(f,cvm_off,elba,esz,path+n+'/')
            else: out.append(dict(path=path+n,lba=elba,size=esz,rec=rec_off,abs=cvm_off+BASE+elba*2048))
        i+=l
    return out
def listing(name,f=None):
    f=f or open(ISO,'rb')
    off=CVMS[name][0]*2048
    f.seek(off+BASE+0x8000);pvd=f.read(2048)
    root=pvd[156:156+34]
    lba=struct.unpack_from('<I',root,2)[0];sz=struct.unpack_from('<I',root,10)[0]
    return read_dir(f,off,lba,sz)
if __name__=='__main__':
    import sys,os,json
    f=open(ISO,'rb');allf={}
    for n in CVMS:
        L=listing(n,f);allf[n]=L
        print(n,len(L),sum(x['size'] for x in L))
        if '-x' in sys.argv:
            for e in L:
                p=os.path.join('work','ext',n,e['path']);os.makedirs(os.path.dirname(p),exist_ok=True)
                f.seek(e['abs']);open(p,'wb').write(f.read(e['size']))
    json.dump(allf,open('work/cvm_list.json','w'),indent=0)
