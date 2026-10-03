import sys,glob,os
from PIL import Image,ImageDraw
def sheet(paths,out,maxw=1600,th=160):
    ims=[]
    for p in paths:
        im=Image.open(p).convert('RGBA');s=min(1,th/im.height,400/im.width);im=im.resize((max(1,int(im.width*s)),max(1,int(im.height*s))))
        bg=Image.new('RGBA',im.size,(60,60,90,255));bg.alpha_composite(im);ims.append((os.path.basename(p),bg))
    x=y=0;rh=0;pos=[]
    for n,im in ims:
        if x+im.width>maxw: x=0;y+=rh+14;rh=0
        pos.append((x,y));x+=im.width+4;rh=max(rh,im.height)
    S=Image.new('RGB',(maxw,y+rh+14),(20,20,20));D=ImageDraw.Draw(S)
    for (n,im),(x,y) in zip(ims,pos): S.paste(im,(x,y+12));D.text((x,y),n[:28],fill=(255,255,0))
    S.save(out)
if __name__=='__main__':
    os.makedirs('work/sheets',exist_ok=True)
    for d in sorted(glob.glob('work/tex/*')):
        ps=sorted(glob.glob(d+'/*.png'))
        name=os.path.basename(d)
        if any(name.startswith(p) for p in sys.argv[1:]) or not sys.argv[1:]:
            for i in range(0,len(ps),60): sheet(ps[i:i+60],'work/sheets/%s_%d.png'%(name,i//60))
