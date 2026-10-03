"""BOOTDAT container: top MRG(6) -> entry0 = 11 string tables"""
import struct
def u(d,o): return struct.unpack_from('<I',d,o)[0]
def parse_mrg(d):
    n=u(d,0);offs=[u(d,4+4*i) for i in range(n)]
    return n,offs
def tables(d):
    """returns list of (table_offset, [raw strings])"""
    b=0x20;n=u(d,b);subs=[u(d,b+4+4*i) for i in range(n)]
    ends=subs[1:]+[u(d,0x1c)]
    res=[]
    for s,e in zip(subs,ends):
        o=b+s;cnt=u(d,o)//4
        offs=[u(d,o+4*i) for i in range(cnt)]
        strs=[]
        for of in offs:
            z=d.index(b'\0',o+of);strs.append(d[o+of:z])
        res.append(strs)
    return res

def a4(n,a=4): return (n+a-1)//a*a
def build_table(strs):
    n=len(strs);hdr=4*n;offs=[];body=bytearray()
    for s in strs:
        offs.append(hdr+len(body));body+=s+b'\0'
    return struct.pack('<%dI'%n,*offs)+bytes(body)
def rebuild(d,new_tables):
    """d: original BOOTDAT decompressed. new_tables: list of 11 lists of raw bytes"""
    n,offs=parse_mrg(d);top_extra=u(d,0x1c)
    # entry0
    tabs=[build_table(t) for t in new_tables]
    m=len(tabs);hdr=4+4*m+4
    e0=bytearray();soffs=[]
    pos=hdr
    for t in tabs:
        soffs.append(pos);e0+=t+bytes(a4(len(t))-len(t));pos=hdr+len(e0)
    e0=struct.pack('<I',m)+struct.pack('<%dI'%m,*soffs)+struct.pack('<I',len(tabs[0]))+bytes(e0)
    e0len=len(e0)
    old_e1=offs[1]
    new_e1=a4(0x20+len(e0),0x100)
    delta=new_e1-old_e1
    delta=(delta+0xff)//0x100*0x100 if delta%0x100 else delta
    new_e1=old_e1+delta
    out=bytearray(d[:0x20]);out+=e0;out+=bytes(new_e1-len(out));out+=d[old_e1:]
    noffs=[0x20]+[o+delta for o in offs[1:]]
    struct.pack_into('<%dI'%n,out,4,*noffs);struct.pack_into('<I',out,0x1c,e0len)
    return bytes(out)
