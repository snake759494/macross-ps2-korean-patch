"""Apply texture translation specs: translation/tex/*.json
spec: {"file":"dec/JPN/MENU_AUTH.BIN","off":"2209a0","boxes":"ov json or null","clear":[..] or null,
       "defaults":{size,font,color_idx,stroke,stroke_idx,align},
       "items":[{"b":id or [ids] or [x0,y0,x1,y1]-as-"box", "t":"text", ...overrides}]}"""
import sys,os,json,glob,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import texedit
def union(bs): return [min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)]
def apply_spec(buf,spec):
    t=texedit.Tex(buf,int(spec['off'],16))
    boxes=json.load(open(spec['boxes'])) if spec.get('boxes') else []
    D=spec.get('defaults',{})
    for it in spec['items']:
        o=dict(D);o.update(it)
        if 'box' in o: box=o['box']
        else:
            ids=o['b'] if isinstance(o['b'],list) else [o['b']];box=union([boxes[i] for i in ids])
        g=o.get('grow',[0,0,0,0]);box=[max(0,box[0]-g[0]),max(0,box[1]-g[1]),min(t.w,box[2]+g[2]),min(t.h,box[3]+g[3])]
        color=tuple(t.pal[o['color_idx']]) if 'color_idx' in o else (tuple(o['color']) if 'color' in o else None)
        sc=tuple(t.pal[o['stroke_idx']]) if 'stroke_idx' in o else (tuple(o['stroke_color']) if 'stroke_color' in o else None)
        o['t']=o['t'].replace('・','·').replace('～','~')
        n=o['t'].count('\n')+1;size=o.get('size')
        lhm=o.get('lh_mul')
        if lhm is None and n>1 and size: lhm=(box[3]-box[1])/n/size
        texedit.render_into(t,box,o['t'],size=size,color=color,align=o.get('align','l'),font=o.get('font','eb'),
            bgidx=o.get('bg'),valign=o.get('valign','c'),stroke=o.get('stroke',0),stroke_color=sc,dx=o.get('dx',0),dy=o.get('dy',0),
            clear=o.get('clear'),lh_mul=lhm or 1.18,pad=o.get('pad',1))
    t.save()
    return t
def preview(t,path):
    from PIL import Image
    im=Image.fromarray(t.rgba());bg=Image.new('RGBA',im.size,(30,30,60,255));bg.alpha_composite(im);bg.save(path)
if __name__=='__main__':
    # build all: groups by file, write work/out tree
    specs=sorted(glob.glob('translation/tex/*.json'))
    only=sys.argv[1:] 
    byfile={}
    for p in specs:
        s=json.load(open(p,encoding='utf8'))
        for sp in (s if isinstance(s,list) else [s]): byfile.setdefault(sp['file'],[]).append((p,sp))
    os.makedirs('work/texprev',exist_ok=True)
    for f,lst in byfile.items():
        buf=bytearray(open('work/'+f,'rb').read())
        for p,sp in lst:
            t=apply_spec(buf,sp)
            preview(t,'work/texprev/%s_%s.png'%(os.path.basename(f),sp['off']))
        os.makedirs('work/texout/'+os.path.dirname(f),exist_ok=True)
        open('work/texout/'+f,'wb').write(buf)
        print('patched',f,len(lst))
