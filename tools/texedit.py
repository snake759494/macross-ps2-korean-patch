"""Texture text replacement for TIM2 (swizzled 4/8bpp)."""
import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import tim2,gs
from PIL import Image,ImageDraw,ImageFont
FONTS={'b':'NanumSquareNeo-cBd.ttf','eb':'NanumSquareNeo-dEb.ttf','h':'NanumSquareNeo-eHv.ttf','r':'NanumSquareNeo-bRg.ttf'}
def tvv(b,w,h):
    a=np.frombuffer(b,np.uint8).reshape(h,w).astype(int)
    return (np.diff(a,axis=0)!=0).sum()+(np.diff(a,axis=1)!=0).sum()
class Tex:
    def __init__(s,buf,off):
        s.buf=buf;s.g=tim2.parse(buf,off)[0];g=s.g
        s.w,s.h,s.t=g['w'],g['h'],g['itype']
        raw=bytes(buf[g['img_off']:g['img_off']+g['img_size']])
        lin=raw[:s.w*s.h] if s.t==5 else bytes(v for b in raw[:s.w*s.h//2] for v in (b&15,b>>4))
        s.raw_n=len(raw);cands=[(tvv(lin,s.w,s.h),None,lin)]
        for W in sorted({s.w//2,16,32,64}):
            try:
                sw=(gs.unswizzle4_w if s.t==4 else gs.unswizzle8_w)(raw,s.w,s.h,W)
                if len(sw)==s.w*s.h and (gs.swizzle4_w if s.t==4 else gs.swizzle8_w)(sw,s.w,s.h,W,len(raw))==raw:
                    cands.append((tvv(sw,s.w,s.h)-(1 if W==s.w//2 else 0),W,sw))
            except Exception: pass
        cands.sort(key=lambda c:c[0]);_,s.W32,best=cands[0]
        s.swz=s.W32 is not None
        s.idx=np.frombuffer(best,np.uint8).reshape(s.h,s.w).copy()
        s.pal=np.array(tim2.clut_rgba(buf,g),float)
    def rgba(s):
        p=s.pal.copy();p[:,3]=np.minimum(255,p[:,3]*2);return p[s.idx].astype(np.uint8)
    def save(s):
        g=s.g;flat=s.idx.ravel()
        if s.swz: data=(gs.swizzle4_w if s.t==4 else gs.swizzle8_w)(bytes(flat),s.w,s.h,s.W32,s.raw_n)
        else:
            data=bytes(flat) if s.t==5 else bytes((int(flat[i])&15)|((int(flat[i+1])&15)<<4) for i in range(0,len(flat),2))
        s.buf[g['img_off']:g['img_off']+len(data)]=data
def detect_lines(rgba,thr=60,gap=2,minh=4,a=None):
    """returns row bands with visible content (alpha*lum)"""
    if a is None: a=rgba[...,3].astype(float)/255*rgba[...,:3].max(-1)
    rows=(a>thr).sum(1)>0
    bands=[];y=0;H=len(rows)
    while y<H:
        if rows[y]:
            y0=y
            while y<H and (rows[y] or any(rows[y:y+gap+1])): y+=1
            if y-y0>=minh: bands.append([y0,y])
        y+=1
    out=[]
    for y0,y1 in bands:
        cols=np.where((a[y0:y1]>thr).any(0))[0];out.append([int(cols[0]),y0,int(cols[-1])+1,y1])
    return out
def render_into(tex,box,text,size=None,color=None,align='l',font='eb',bgidx=None,valign='c',stroke=0,stroke_color=None,dx=0,dy=0,squeeze=True,pad=1,clear=None,lh_mul=1.18):
    x0,y0,x1,y1=box;W=x1-x0;H=y1-y0
    reg=tex.idx[y0:y1,x0:x1]
    if bgidx=='mode': bgidx=int(np.bincount(reg.ravel()).argmax())
    if bgidx is None:
        border=np.concatenate([reg[0],reg[-1],reg[:,0],reg[:,-1]])
        bgidx=np.bincount(border).argmax()
    pal=tex.pal
    if color is None:
        # brightest frequently used color in region
        cnt=np.bincount(reg.ravel(),minlength=len(pal))
        cand=[i for i in range(len(pal)) if cnt[i]>max(3,cnt.sum()*0.01) and i!=bgidx]
        color=tuple(pal[max(cand,key=lambda i:pal[i][:3].sum()*min(pal[i][3],128))]) if cand else (255,255,255,128)
    if clear is None: reg[:]=bgidx;free=np.ones(reg.shape,bool)
    else:
        m0=np.isin(reg,clear);reg[m0]=bgidx;free=(reg==bgidx)
    size=size or int(H*0.85)
    S=4;F=ImageFont.truetype(FONTS.get(font,font),size*S)
    lines=text.split('\n')
    def measure(F):
        D=ImageDraw.Draw(Image.new('L',(1,1)));return [D.textbbox((0,0),l,font=F,stroke_width=stroke*S) for l in lines]
    bbs=measure(F)
    tw=max(b[2]-b[0] for b in bbs) if lines else 1
    asc,desc=F.getmetrics();lh=int(size*S*lh_mul) if len(lines)>1 else (asc+desc)
    th=lh*(len(lines)-1)+ (asc+desc)
    sx=1.0
    if squeeze and tw>W*S-2*pad*S: sx=(W*S-2*pad*S)/tw
    if th>H*S: # shrink font
        f=H*S/th;F=ImageFont.truetype(FONTS.get(font,font),max(6,int(size*S*f)));size=int(size*f);bbs=measure(F);asc,desc=F.getmetrics();lh=int(size*S*lh_mul);th=lh*(len(lines)-1)+asc+desc;tw=max(b[2]-b[0] for b in bbs)
        if tw>W*S-2*pad*S: sx=(W*S-2*pad*S)/tw
    cw=int(max(tw,1)+8*S)
    im=Image.new('L',(cw,max(th,1)+8*S),0);D=ImageDraw.Draw(im)
    st=None
    if stroke: st=Image.new('L',im.size,0);DS=ImageDraw.Draw(st)
    for k,(l,b) in enumerate(zip(lines,bbs)):
        lw=b[2]-b[0]
        xx={'l':0,'c':(tw-lw)//2,'r':tw-lw}[align]-b[0]+4*S
        yy=k*lh+4*S
        D.text((xx,yy),l,font=F,fill=255)
        if stroke: DS.text((xx,yy),l,font=F,fill=255,stroke_width=stroke*S,stroke_fill=255)
    nw=max(1,int(im.width*sx/S));nh=max(1,im.height//S)
    m=np.array(im.resize((nw,nh),Image.LANCZOS)).astype(float)/255
    sm=np.array(st.resize((nw,nh),Image.LANCZOS)).astype(float)/255 if stroke else None
    tw2=int(tw*sx/S);th2=th//S
    ox={'l':pad,'c':(W-tw2)//2,'r':W-tw2-pad}[align]-4+dx
    oy={'c':(H-th2)//2,'t':0,'b':H-th2}[valign]-4+dy
    bg=pal[bgidx];fg=np.array(color,float)
    sc=np.array(stroke_color if stroke_color is not None else (0,0,0,128),float)
    # palette-quantize blended colors
    for yy in range(nh):
        ty=oy+yy
        if not 0<=ty<H: continue
        for xx in range(nw):
            tx=ox+xx
            if not 0<=tx<W: continue
            a=m[yy,xx];s_=sm[yy,xx] if stroke else 0
            if a<0.04 and s_<0.04: continue
            if not free[ty,tx]: continue
            base=bg*(1-s_)+sc*s_ if stroke else bg
            c=base*(1-a)+fg*a
            d=((pal-c)**2*np.array([1,1,1,2])).sum(1)
            reg[ty,tx]=int(d.argmin())
    return color

def detect_words(rgba,thr=60,gap=2,colgap=8,minh=4,a=None):
    if a is None: a=rgba[...,3].astype(float)/255*rgba[...,:3].max(-1)
    out=[]
    for x0,y0,x1,y1 in detect_lines(rgba,thr,gap,minh,a):
        cols=(a[y0:y1]>thr).any(0)
        x=0;W=len(cols)
        while x<W:
            if cols[x]:
                s=x;run=0
                while x<W:
                    if cols[x]: run=0
                    else:
                        run+=1
                        if run>=colgap: break
                    x+=1
                e=x-run
                sub=(a[y0:y1,s:e]>thr).any(1);ys=np.where(sub)[0]
                out.append([s,y0+int(ys[0]),e,y0+int(ys[-1])+1])
            x+=1
    return out
def overlay(rgba,boxes,path,scale=2):
    from PIL import ImageDraw
    im=Image.fromarray(rgba).convert('RGBA');bg=Image.new('RGBA',im.size,(30,30,60,255));bg.alpha_composite(im)
    im=bg.resize((im.width*scale,im.height*scale),Image.NEAREST);D=ImageDraw.Draw(im)
    for i,(x0,y0,x1,y1) in enumerate(boxes):
        D.rectangle([x0*scale,y0*scale,x1*scale-1,y1*scale-1],outline=(255,0,0,255))
        D.text((x0*scale+1,y0*scale+1),str(i),fill=(255,255,0,255))
    im.save(path)
if __name__=='__main__':
    f,off=sys.argv[1],int(sys.argv[2],16);cg=int(sys.argv[3]) if len(sys.argv)>3 else 8
    t=Tex(bytearray(open(f,'rb').read()),off)
    A=None
    if len(sys.argv)>4: A=np.isin(t.idx,[int(x) for x in sys.argv[4].split(',')]).astype(float)*255
    B=detect_words(t.rgba(),colgap=cg,a=A)
    os.makedirs('work/ov',exist_ok=True);p='work/ov/%s_%x.png'%(os.path.basename(f),off);overlay(t.rgba(),B,p)
    json.dump(B,open(p[:-4]+'.json','w'));print(p,len(B))
