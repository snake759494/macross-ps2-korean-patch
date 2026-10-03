"""Patch files inside CVMs and relocate grown CVMs into ETC.CVM's unused space."""
import struct,sys,os,shutil
sys.path.insert(0,os.path.dirname(__file__))
import cvm
SEC=2048
OUTER={'JPN':'JPN.CVM','BIN':'BIN.CVM','MOV':'MOV.CVM','ADXJ':'ADXJ.CVM','ETC':'ETC.CVM'}
def outer_records(iso):
    import pycdlib
    p=pycdlib.PyCdlib();p.open(iso);res={}
    for ch in p.list_children(iso_path='/'):
        n=ch.file_identifier().decode()
        if n in ('.','..'):continue
        res[n.split(';')[0]]=dict(lba=ch.extent_location(),size=ch.get_data_length(),rec=None)
    # find raw record offsets in root dir
    pvd=open(iso,'rb');pvd.seek(16*SEC);pv=pvd.read(SEC)
    rl=struct.unpack_from('<I',pv,156+2)[0];rs=struct.unpack_from('<I',pv,156+10)[0]
    pvd.seek(rl*SEC);d=pvd.read(rs);i=0
    while i<len(d):
        l=d[i]
        if l==0: i=(i//SEC+1)*SEC;continue
        nm=d[i+33:i+33+d[i+32]].decode('ascii','replace').split(';')[0]
        if nm in res: res[nm]['rec']=rl*SEC+i
        i+=l
    p.close();return res
def set_rec(f,rec,lba,size):
    f.seek(rec+2);f.write(struct.pack('<I',lba)+struct.pack('>I',lba)+struct.pack('<I',size)+struct.pack('>I',size))
def patch_cvm(cvmdata,files):
    """files: {path: bytes}. returns new cvm bytes"""
    d=bytearray(cvmdata);B=cvm.BASE
    # entries via parse on bytes
    import io
    lst=_listing(bytes(d))
    end=len(d)
    for e in lst:
        if e['path'] not in files: continue
        nb=files.pop(e['path'])
        alloc=(e['size']+SEC-1)//SEC*SEC
        if len(nb)<=alloc:
            pos=B+e['lba']*SEC;d[pos:pos+alloc]=nb+bytes(alloc-len(nb));lba=e['lba']
        else:
            lba=(len(d)-B+SEC-1)//SEC
            d+=bytes(B+lba*SEC-len(d));d+=nb+bytes((-len(nb))%SEC)
        r=e['rec']
        d[r+2:r+10]=struct.pack('<I',lba)+struct.pack('>I',lba);d[r+10:r+18]=struct.pack('<I',len(nb))+struct.pack('>I',len(nb))
    assert not files,files.keys()
    tot=len(d)
    struct.pack_into('>Q',d,0x20,tot)
    struct.pack_into('>I',d,0x808,tot-0x80c)
    struct.pack_into('>I',d,0x834,tot-0x1800)
    pv=B+0x8000;vs=(tot-B)//SEC
    struct.pack_into('<I',d,pv+80,vs);struct.pack_into('>I',d,pv+84,vs)
    return bytes(d)
def _listing(d):
    B=cvm.BASE;out=[]
    pv=d[B+0x8000:B+0x8800];root=pv[156:190]
    def rd(lba,size,path):
        dd=d[B+lba*SEC:B+lba*SEC+size];i=0
        while i<len(dd):
            l=dd[i]
            if l==0: i=(i//SEC+1)*SEC;continue
            r=dd[i:i+l];el=struct.unpack_from('<I',r,2)[0];es=struct.unpack_from('<I',r,10)[0]
            nm=r[33:33+r[32]]
            if nm not in (b'\0',b'\1'):
                n=nm.decode().split(';')[0]
                if r[25]&2: rd(el,es,path+n+'/')
                else: out.append(dict(path=path+n,lba=el,size=es,rec=B+lba*SEC+i))
            i+=l
    rd(struct.unpack_from('<I',root,2)[0],struct.unpack_from('<I',root,10)[0],'')
    return out
def read_cvm(iso,name):
    l,s=cvm.CVMS[name];f=open(iso,'rb');f.seek(l*SEC);return f.read(s)
def build(src_iso,dst_iso,cvm_files,root_files):
    """cvm_files: {CVMNAME:{path:bytes}}, root_files: {name: bytes} (same size or smaller only)"""
    if not os.path.exists(dst_iso) or os.path.getsize(dst_iso)!=os.path.getsize(src_iso): shutil.copyfile(src_iso,dst_iso)
    recs=outer_records(src_iso)
    etc=recs['ETC.CVM'];free=etc['lba']
    with open(dst_iso,'r+b') as f:
        # restore originals for every CVM first (idempotent rebuild)
        src=open(src_iso,'rb')
        for nm,r in recs.items():
            src.seek(r['lba']*SEC);data=src.read(r['size']);f.seek(r['lba']*SEC);f.write(data);set_rec(f,r['rec'],r['lba'],r['size'])
        src.seek(etc['lba']*SEC);f.seek(etc['lba']*SEC);
        left=etc['size']
        while left>0:
            ch=src.read(min(left,1<<24));f.write(ch);left-=len(ch)
        for nm,files in cvm_files.items():
            if not files: continue
            r=recs[OUTER[nm]];new=patch_cvm(read_cvm(src_iso,nm),dict(files))
            if len(new)<=(r['size']+SEC-1)//SEC*SEC: lba=r['lba']
            else:
                lba=free;free+=(len(new)+SEC-1)//SEC
                assert free<=etc['lba']+etc['size']//SEC,'ETC space exhausted'
            f.seek(lba*SEC);f.write(new+bytes((-len(new))%SEC));set_rec(f,r['rec'],lba,len(new))
            print('CVM',nm,'lba',lba,'size',len(new),'(orig',r['size'],')')
        for nm,data in root_files.items():
            r=recs[nm];assert len(data)<=(r['size']+SEC-1)//SEC*SEC
            f.seek(r['lba']*SEC);f.write(data);set_rec(f,r['rec'],r['lba'],len(data))
