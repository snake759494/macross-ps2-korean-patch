import sys,os,json,glob,re;sys.path.insert(0,'tools');import texedit,tim2
from PIL import Image
inv=json.load(open('work/tex_inventory.json'))
out={}
for k,L in inv.items():
    if not any(s in k for s in sys.argv[1:]): continue
    d=bytearray(open('work/'+k,'rb').read())
    for a,i,w,h,t in L:
        if i!=0 or t not in (4,5): continue
        try: T=texedit.Tex(d,a)
        except Exception as e: continue
        im=Image.fromarray(T.rgba());p='work/tex2/%s/%x.png'%(k.replace('/','_'),a)
        os.makedirs(os.path.dirname(p),exist_ok=True);im.save(p);out.setdefault(k,[]).append([a,w,h,T.W32])
json.dump(out,open('work/tex2_inv.json','w'))
print(sum(len(v) for v in out.values()))
