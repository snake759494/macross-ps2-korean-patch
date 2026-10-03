import sys,os;sys.path.insert(0,os.path.dirname(__file__))
import font
FIX={'~':'～','‘':"'",'’':"'",'“':'"','”':'"','…':'…','·':'・','-':'-'}
def enc(s,bad=None):
    out=bytearray()
    for ch in s:
        if ch in font.CHARMAP: out+=font.CHARMAP[ch];continue
        c=FIX.get(ch,ch)
        try: out+=c.encode('cp932')
        except UnicodeEncodeError:
            if bad is not None: bad.add(ch)
            out+=b'?'
    return bytes(out)

def cw(ch):
    return 10 if ord(ch)<0x80 else 20
def wrap(s,W):
    out=[]
    for para in s.split('\n'):
        words=para.split(' ');line=''
        for w in words:
            cand=(line+' '+w) if line else w
            if sum(cw(c) for c in cand)<=W or not line: line=cand
            else: out.append(line);line=w
        out.append(line)
    return '\n'.join(out)
