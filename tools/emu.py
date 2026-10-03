"""PCSX2 window capture + key input via win32 (ctypes)."""
import ctypes,ctypes.wintypes as W,time,sys
from PIL import ImageGrab
u=ctypes.windll.user32
def find():
    res=[]
    @ctypes.WINFUNCTYPE(ctypes.c_bool,W.HWND,W.LPARAM)
    def cb(h,l):
        n=u.GetWindowTextLengthW(h)
        if n and u.IsWindowVisible(h):
            b=ctypes.create_unicode_buffer(n+1);u.GetWindowTextW(h,b,n+1)
            pid=W.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(pid))
            res.append((h,b.value))
        return True
    u.EnumWindows(cb,0)
    return [r for r in res if 'PCSX2' in r[1] or 'Macross' in r[1] or 'マクロス' in r[1] or 'SLPM' in r[1]]
def grab(path,h=None):
    h=h or find()[0][0]
    r=W.RECT();u.GetClientRect(h,ctypes.byref(r));p=W.POINT(0,0);u.ClientToScreen(h,ctypes.byref(p))
    u.SetForegroundWindow(h);time.sleep(0.3)
    im=ImageGrab.grab((p.x,p.y,p.x+r.right,p.y+r.bottom),all_screens=True);im.save(path);return im
VK={'up':0x26,'down':0x28,'left':0x25,'right':0x27,'enter':0x0d,'esc':0x1b,'space':0x20}
def key(k,hold=0.3,h=None):
    h=h or find()[0][0];u.SetForegroundWindow(h);time.sleep(0.1)
    vk=VK.get(k) or ord(k.upper())
    sc=u.MapVirtualKeyW(vk,0)
    ext=1 if k in ('up','down','left','right') else 0
    u.keybd_event(vk,sc,ext,0);time.sleep(hold);u.keybd_event(vk,sc,2|ext,0);time.sleep(0.1)
if __name__=='__main__':
    print(find())
    if len(sys.argv)>2 and sys.argv[1]=='grab': grab(sys.argv[2])
    if len(sys.argv)>2 and sys.argv[1]=='key':
        for k in sys.argv[2:]: key(k);time.sleep(0.4)
