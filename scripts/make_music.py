# Musique originale synthétisée (aucun droit d'auteur). Usage: python3 -I make_music.py out.wav seconds [bpm] [style]
import sys, numpy as np, wave
out=sys.argv[1]; dur=float(sys.argv[2]); bpm=float(sys.argv[3]) if len(sys.argv)>3 else 108; style=sys.argv[4] if len(sys.argv)>4 else "groove"
sr=44100; n=int(dur*sr); t=np.arange(n)/sr; beat=60/bpm; mix=np.zeros(n)
rng=np.random.default_rng(7)
def add(sig,start):
    i=int(start*sr)
    if i>=n: return
    e=min(n,i+len(sig)); mix[i:e]+=sig[:e-i]
def kick():
    L=int(.28*sr); tt=np.arange(L)/sr; f=45+90*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/sr
    return np.sin(ph)*np.exp(-tt*9)*1.0
def hat(open_=False):
    L=int((.16 if open_ else .05)*sr); tt=np.arange(L)/sr; x=rng.standard_normal(L)
    x=np.diff(x,prepend=0); return x*np.exp(-tt*(25 if open_ else 80))*.18
def snare():
    L=int(.2*sr); tt=np.arange(L)/sr; x=rng.standard_normal(L)*np.exp(-tt*22)*.5+np.sin(2*np.pi*190*tt)*np.exp(-tt*30)*.4; return x
def bass(f,d):
    L=int(d*sr); tt=np.arange(L)/sr; env=np.minimum(1,tt*80)*np.exp(-tt*3.2)
    return (np.sin(2*np.pi*f*tt)+.3*np.sin(2*np.pi*2*f*tt))*env*.55
def pluck(f,d):
    L=int(d*sr); tt=np.arange(L)/sr; env=np.minimum(1,tt*200)*np.exp(-tt*5)
    return (np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*2*f*tt)+.25*np.sin(2*np.pi*3*f*tt))*env*.16
def pad(fs,d):
    L=int(d*sr); tt=np.arange(L)/sr; env=np.minimum(1,tt*3)*np.minimum(1,(d-tt)*3)
    return sum(np.sin(2*np.pi*f*tt+i) for i,f in enumerate(fs))*env*.05
nm={'A':220.0,'C':261.63,'D':293.66,'E':329.63,'F':349.23,'G':392.0,'B':246.94}
prog=[('A',[220,261.63,329.63]),('F',[174.61,220,261.63]),('C',[261.63,329.63,392]),('G',[196,246.94,293.66])]
bars=int(dur/(beat*4))+2
for b in range(bars):
    t0=b*beat*4; root,ch=prog[b%4]; rf=ch[0]/2
    add(pad(ch,beat*4),t0)
    for k in range(4):
        add(kick(),t0+k*beat)
        if k in (1,3): add(snare(),t0+k*beat)
    for s in range(8):
        add(hat(s%2==1),t0+s*beat/2)
    for q,(off,mult) in enumerate([(0,1),(.75,1),(1.5,1.5),(2.5,1),(3,2)]):
        add(bass(rf*mult,beat*.7),t0+off*beat)
    arp=[ch[0]*2,ch[1]*2,ch[2]*2,ch[1]*2]
    for s in range(8): add(pluck(arp[s%4]*(2 if s%8>=4 else 1),beat*.5),t0+s*beat/2)
# sidechain léger + fondu
mix*=1-0.25*np.exp(-((t%beat)*14))
fade=np.minimum(1,t/0.4)*np.minimum(1,(dur-t)/1.2); mix*=fade
mix=np.tanh(mix*1.3); mix/=np.max(np.abs(mix)); mix*=0.8
w=wave.open(out,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
