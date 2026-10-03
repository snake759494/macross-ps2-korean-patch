"""CRICMP 2.10 (mode 0) codec, reversed from SLPM_654.05 0x2e8320/0x2e8930."""
import struct
def decompress(d):
    assert d[:6]==b'CRICMP'
    usize=struct.unpack_from('<I',d,0x14)[0];base=struct.unpack_from('<I',d,0x18)[0]
    p=base+2
    ngroups=struct.unpack_from('>I',d,p)[0];p+=4
    out=bytearray()
    def group(n):
        nonlocal p
        flags=struct.unpack_from('>H',d,p)[0];p+=2
        for i in range(n):
            w=struct.unpack_from('>H',d,p)[0];p+=2
            if flags>>i&1:
                out.append(w>>8)
                if len(out)>=usize: return
                out.append(w&0xff)
            elif w&0xf000==0:
                out.extend(bytes([out[-1]])*(w+3))
            else:
                ln=(w>>12)+2;off=w&0xfff;s=len(out)-off
                for k in range(ln): out.append(out[s+k])
    for g in range(ngroups): group(16)
    pad=struct.unpack('b',d[p:p+1])[0];rem=struct.unpack('b',d[p+1:p+2])[0];p+=2
    if rem>0: group(rem)
    pass
    return bytes(out[:usize])
def compress(src):
    """greedy LZ: tokens are 2-byte literal pairs, run fills, or copies len 3..17 dist 1..4095"""
    n=len(src);toks=[];i=0
    pad=0
    if n%2: pass
    # hash chain on 3-byte prefixes
    head={};prev=[-1]*n
    def ins(j):
        if j+2<n:
            k=src[j:j+3];prev[j]=head.get(k,-1);head[k]=j
    inserted=0
    while i<n:
        while inserted<i: ins(inserted);inserted+=1
        best=0;bd=0
        # run fill: previous byte repeated
        if i>0:
            r=0;c=src[i-1]
            while i+r<n and src[i+r]==c and r<0xfff+3: r+=1
            if r>=3: best=r;bd=-1
        if i+2<n:
            j=head.get(src[i:i+3],-1);tries=0
            while j>=0 and i-j<=0xfff and tries<256:
                l=0
                while i+l<n and l<17 and src[j+l]==src[i+l]: l+=1
                if l>best or (l==best and bd==-1 and False): best=l;bd=i-j
                if l==17: break
                j=prev[j];tries+=1
        if bd==-1 and best>=3:
            toks.append((0,best-3));i+=best
        elif best>=3 and bd>0:
            toks.append((0,((best-2)<<12)|bd));i+=best
        else:
            a=src[i];b=src[i+1] if i+1<n else 0
            if i+1>=n: pad=1
            toks.append((1,(a<<8)|b));i+=2
    # NB: decoder stops literal at usize so odd final byte works; pad stays 0
    out=bytearray()
    ng=len(toks)//16;rem=len(toks)%16
    out+=b'\x10\x00'+struct.pack('>I',ng)
    def emit(ts):
        fl=0
        for k,(f,_) in enumerate(ts): fl|=f<<k
        out.extend(struct.pack('>H',fl))
        for _,w in ts: out.extend(struct.pack('>H',w))
    for g in range(ng): emit(toks[g*16:g*16+16])
    out+=struct.pack('bb',0,rem)
    if rem: emit(toks[ng*16:])
    hdr=bytearray(b'CRICMP\0\0'+b'2.10'+b'\0'*4)
    hdr+=struct.pack('<IIII',0x20,n,0x20,0)
    while len(out)%4: out.append(0)
    return bytes(hdr+out)
