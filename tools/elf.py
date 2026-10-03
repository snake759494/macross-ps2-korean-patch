import struct,capstone
ELF='work/SLPM_654.05'
D=open(ELF,'rb').read()
BASE=0x100000;FOFF=0x80;TEXT_END=0x100000+0x2cd900
def v2o(v): return v-BASE+FOFF
def o2v(o): return o-FOFF+BASE
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS64|capstone.CS_MODE_LITTLE_ENDIAN)
md32=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32|capstone.CS_MODE_LITTLE_ENDIAN)
R=['zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']
def dis1(v):
    o=v2o(v);w=struct.unpack_from('<I',D,o)[0];op=w>>26
    if op in (0x1e,0x1f):
        imm=w&0xffff;imm=imm-0x10000 if imm&0x8000 else imm
        return ('lq' if op==0x1e else 'sq'),'$%s, %d($%s)'%(R[(w>>16)&31],imm,R[(w>>21)&31])
    for m in (md,md32):
        l=list(m.disasm(D[o:o+4],v))
        if l: return l[0].mnemonic,l[0].op_str
    return '.word',hex(w)
def pr(v,n):
    for k in range(n):
        a=v+4*k;m,o=dis1(a);print('%08x: %s %s'%(a,m,o))
def xrefs(target):
    """find lui/addiu or lui/ori pairs forming target (simple, same reg within 8 insns)"""
    hi=(target+0x8000)>>16;lo=target&0xffff;res=[]
    for o in range(FOFF,v2o(TEXT_END),4):
        w=struct.unpack_from('<I',D,o)[0]
        if w>>26==0xf and (w&0xffff)==hi:
            rt=(w>>16)&31
            for k in range(1,12):
                w2=struct.unpack_from('<I',D,o+4*k)[0]
                op=w2>>26
                if op in (9,0x19,0x23,0x2b,0x24,0x25,0x20,0x21,0x28,0x29,0x37,0x3f,0x31,0x39) and ((w2>>21)&31)==rt and (w2&0xffff)==lo:
                    res.append(o2v(o+4*k));break
    return res
def funcstart(v):
    o=v2o(v)
    while o>FOFF:
        w=struct.unpack_from('<I',D,o)[0]
        if (w&0xffff0000)==0x27bd0000 and (w&0x8000): return o2v(o)
        o-=4
