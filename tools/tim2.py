"""TIM2 parse/write (subset: 4/8bpp indexed with CLUT, 32/24/16bpp)"""
import struct
from PIL import Image
def unswz32(cl):  # CSM1 swizzle for 256-color clut
    out=list(cl)
    for i in range(256):
        j=(i&0xe7)|((i&8)<<1)|((i&16)>>1)
        out[i]=cl[j]
    return out
def parse(d,off=0):
    assert d[off:off+4]==b'TIM2',hex(off)
    n=struct.unpack_from('<H',d,off+6)[0];p=off+(0x80 if d[off+5]==1 else 16);pics=[]
    for k in range(n):
        tot,clsz,imsz,hsz,clc,fmt,mip,ctype,itype,w,h=struct.unpack_from('<IIIHHBBBBHH',d,p)
        g=dict(off=p,total=tot,clut_size=clsz,img_size=imsz,hdr=hsz,clut_colors=clc,ctype=ctype,itype=itype,w=w,h=h,
               img_off=p+hsz,clut_off=p+hsz+imsz,gstex=d[p+0x18:p+0x30])
        pics.append(g);p+=tot
    return pics
def clut_rgba(d,g):
    ct=g['ctype']&0x3f;cs=bool(g['ctype']&0x80);n=g['clut_colors'];o=g['clut_off']
    cols=[]
    for i in range(n):
        if ct==3: r,gg,b,a=d[o+4*i:o+4*i+4]
        elif ct==2: r,gg,b=d[o+3*i:o+3*i+3];a=0x80
        else:
            v=struct.unpack_from('<H',d,o+2*i)[0];r=(v&31)<<3;gg=(v>>5&31)<<3;b=(v>>10&31)<<3;a=0x80 if v>>15 else 0
        cols.append((r,gg,b,a))
    if n==256 and not cs: cols=unswz32(cols)
    return cols
def to_image(d,g):
    w,h=g['w'],g['h'];o=g['img_off'];t=g['itype']
    if t in (4,5):
        cl=clut_rgba(d,g);px=[]
        if t==5: idx=d[o:o+w*h]
        else:
            idx=bytearray()
            for b in d[o:o+w*h//2]: idx+=bytes([b&15,b>>4])
        im=Image.new('RGBA',(w,h))
        im.putdata([(c[0],c[1],c[2],min(255,c[3]*2)) for c in (cl[i] if i<len(cl) else (0,0,0,0) for i in idx)])
        return im,bytes(idx),cl
    if t==3:
        im=Image.frombytes('RGBA',(w,h),d[o:o+w*h*4]);a=im.split()[3].point(lambda v:min(255,v*2));im.putalpha(a);return im,None,None
    if t==2:
        return Image.frombytes('RGB',(w,h),d[o:o+w*h*3]),None,None
    if t==1:
        px=[];import struct as s
        for i in range(w*h):
            v=s.unpack_from('<H',d,o+2*i)[0];px.append(((v&31)<<3,(v>>5&31)<<3,(v>>10&31)<<3,255 if v>>15 else 0))
        im=Image.new('RGBA',(w,h));im.putdata(px);return im,None,None
def set_indices(buf,g,idx):
    o=g['img_off'];w,h=g['w'],g['h']
    if g['itype']==5: buf[o:o+w*h]=bytes(idx)
    else:
        b=bytearray(w*h//2)
        for i in range(0,w*h,2): b[i//2]=(idx[i]&15)|((idx[i+1]&15)<<4)
        buf[o:o+w*h//2]=b
