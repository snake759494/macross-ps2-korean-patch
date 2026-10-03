import sys,re,glob,os,json;sys.path.insert(0,'tools');import tim2,gs
from PIL import Image
import numpy as np
def tv(b,w,h):
    a=np.frombuffer(b,np.uint8).reshape(h,w).astype(int)
    return (np.abs(np.diff(a,axis=0))>0).sum()+(np.abs(np.diff(a,axis=1))>0).sum()
def decode(d,g,swz=True):
    w,h,t=g['w'],g['h'],g['itype'];raw=d[g['img_off']:g['img_off']+g['img_size']]
    idx=None
    if t in (4,5):
        lin=raw[:w*h] if t==5 else bytes(v for b in raw[:w*h//2] for v in (b&15,b>>4))
        try:
            sw=gs.unswizzle4(raw,w,h) if t==4 else gs.unswizzle8(raw,w,h)
            idx=sw if tv(sw,w,h)<tv(lin,w,h) else lin
        except Exception: idx=lin
    if t in (4,5):
        if idx is None:
            idx=raw[:w*h] if t==5 else bytes(v for b in raw[:w*h//2] for v in (b&15,b>>4))
        cl=tim2.clut_rgba(d,g)
        im=Image.new('RGBA',(w,h));im.putdata([(c[0],c[1],c[2],min(255,c[3]*2)) if i<len(cl) else (0,0,0,0) for i in idx for c in [cl[i] if i<len(cl) else (0,0,0,0)]])
        return im
    return tim2.to_image(d,g)[0]
if __name__=='__main__':
    files=sorted(glob.glob('work/dec/*/*'))+sorted(glob.glob('work/ext/*/*.MRG'))+sorted(glob.glob('work/ext/BIN/*.CAT'))+sorted(glob.glob('work/ext/BIN/*.CHRW'))+sorted(glob.glob('work/ext/BIN/*.MSD'))+sorted(glob.glob('work/ext/BIN/*.AUT'))
    inv={}
    for f in files:
        d=open(f,'rb').read();key=f.replace(os.sep,'/').split('work/')[1]
        lst=[]
        for m in re.finditer(b'TIM2',d):
            try: ps=tim2.parse(d,m.start())
            except Exception: continue
            for k,g in enumerate(ps):
                if not(0<g['w']<=1024 and 0<g['h']<=1024): continue
                try: im=decode(d,g)
                except Exception as e: continue
                if im is None: continue
                out='work/tex/%s/%x_%d.png'%(key.replace('/','_'),m.start(),k)
                os.makedirs(os.path.dirname(out),exist_ok=True);im.save(out)
                lst.append([m.start(),k,g['w'],g['h'],g['itype']])
        if lst: inv[key]=lst
    json.dump(inv,open('work/tex_inventory.json','w'))
    print(len(inv),sum(len(v) for v in inv.values()))
