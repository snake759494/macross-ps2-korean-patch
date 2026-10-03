"""Build Korean glyphs into CRSDAT.MRG (Sony FNT 20x20 4bpp). Hangul KS X 1001 2350 -> JIS rows 16..40"""
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
FONT_BASE=0x3ec00+0xd8
def hangul_list():
    out=[]
    for hi in range(0xb0,0xc9):
        for lo in range(0xa1,0xff): out.append(bytes([hi,lo]).decode('euc-kr'))
    return out
HANGUL=hangul_list()
def jis_to_sjis(row,cell):
    c1=(row+1)//2+(0x80 if row<=62 else 0xc0)
    if row%2: c2=cell+(0x3f if cell<=63 else 0x40)
    else: c2=cell+0x9e
    return bytes([c1,c2])
CHARMAP={}
for i,ch in enumerate(HANGUL): CHARMAP[ch]=jis_to_sjis(16+i//94,1+i%94)
def glyph_index(row,cell): return (row-1)*94+cell-1
def render(ch,fontpath='NanumSquareNeo-cBd.ttf',size=17,dy=0):
    F=ImageFont.truetype(fontpath,size)
    im=Image.new('L',(20*4,20*4),0);D=ImageDraw.Draw(im)
    F4=ImageFont.truetype(fontpath,size*4)
    bb=D.textbbox((0,0),ch,font=F4)
    x=(80-(bb[2]-bb[0]))//2-bb[0];y=(80-(bb[3]-bb[1]))//2-bb[1]+dy*4
    D.text((x,y),ch,font=F4,fill=255)
    a=np.array(im.resize((20,20),Image.LANCZOS)).astype(float)/255
    body=np.clip(a*1.15,0,1)
    m=(a>0.2).astype(np.uint8)*255
    halo=np.array(Image.fromarray(m).filter(ImageFilter.MaxFilter(3)))>0
    v=np.where(body>0.15, 4+np.round(body*11), np.where(halo,4,0))
    return np.clip(v,0,15).astype(np.uint8)
def pack(a):
    f=a.ravel();return bytes((int(f[i])&15)|((int(f[i+1])&15)<<4) for i in range(0,400,2))
def build(src,dst=None,fontpath='NanumSquareNeo-cBd.ttf'):
    d=bytearray(src)
    for i,ch in enumerate(HANGUL):
        gi=glyph_index(16+i//94,1+i%94)
        d[FONT_BASE+gi*200:FONT_BASE+gi*200+200]=pack(render(ch,fontpath))
    return bytes(d)
