# Vidéo verticale animée 1080x1920 + musique. Usage: python3 -I make_video.py spec.json out.mp4
# spec: {"bpm":108,"scenes":[
#  {"type":"hook","title":"C'est quoi la Bourse ?","sub":"Explication en 20 secondes","dur":2.6},
#  {"type":"points","title":"En clair","items":["texte 1","texte 2"],"dur":6},
#  {"type":"stats","title":"En chiffres","stats":[["48","sociétés cotées"],["21 400","Mds FCFA de capitalisation"]],"dur":4},
#  {"type":"outro","title":"Suis BRVM Éclair","sub":"La Bourse de l'UEMOA, en clair.","dur":2.6}]}
import json,sys,os,subprocess,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
spec=json.load(open(sys.argv[1])); out=sys.argv[2]
W,H,FPS=1080,1920,30
def eo(x): x=max(0,min(1,x)); return 1-(1-x)**3
def eb(x):
    x=max(0,min(1,x)); c=1.70158; return 1+(c+1)*(x-1)**3+c*(x-1)**2
F={k:{} for k in ()}
def fnt(w,s):
    k=(w,s)
    if k not in F: F[k]=font(w,s)
    return F[k]
def bg(d,t,idx):
    d.rectangle((0,0,W,H),fill=NAVY)
    for i in range(5):
        r=220+i*130+int(25*math.sin(t*1.2+i)); cx=W*(0.15+0.7*((i*0.37+idx*0.21)%1)) + 40*math.sin(t*.8+i)
        cy=H*(0.12+0.16*i)+60*math.cos(t*.7+i)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=NAVY2,width=6)
    bolt(d,W-380,H-640+int(20*math.sin(t*1.5)),560,NAVY2)
def ctext(d,txt,y,f,fill,alpha=1,dy=0):
    col=tuple(int(NAVY[i]+(fill[i]-NAVY[i])*alpha) for i in range(3))
    d.text(((W-tw(d,txt,f))/2,y+dy),txt,font=f,fill=col)
def brand(d,t):
    bolt(d,60,60,70,ORANGE); d.text((150,66),"BRVM ÉCLAIR",font=fnt("ExtraBold",44),fill=OFF)
def footer(d,prog):
    d.rectangle((0,H-14,int(W*prog),H),fill=ORANGE)
    f=fnt("Bold",26); t="Information, pas un conseil en investissement"
    d.text(((W-tw(d,t,f))/2,H-110),t,font=f,fill=MUTED)
def pill(d,txt,y,t0,t):
    f=fnt("Bold",34); w=tw(d,txt,f)+60; a=eb((t-t0)/0.45)
    x=(W-w)/2; d.rounded_rectangle((x,y+(1-a)*30,x+w,y+66+(1-a)*30),radius=33,fill=ORANGE)
    d.text((x+30,y+11+(1-a)*30),txt,font=f,fill=NAVY)
def scene(d,sc,t,idx):
    ty=sc["type"]
    if ty=="hook":
        pill(d,"LE MOT DU JOUR" if sc.get("tag") is None else sc["tag"],520,0.0,t)
        f=fnt("ExtraBold",118); lines=wrap(d,sc["title"],f,940); y=640
        for i,l in enumerate(lines):
            a=eb((t-0.15-i*0.18)/0.5); ctext(d,l,y,f,OFF if i<len(lines)-1 else ORANGE,min(1,a*1.4),(1-a)*90); y+=140
        if sc.get("sub"):
            a=eo((t-0.9)/0.5); ctext(d,sc["sub"],y+40,fnt("Medium",44),MUTED,a,(1-a)*30)
    elif ty=="points":
        ctext(d,sc["title"].upper(),300,fnt("ExtraBold",78),ORANGE,eo(t/0.4),(1-eo(t/0.4))*-40)
        d.rectangle((W/2-80,400,W/2+80,408),fill=ORANGE)
        n=len(sc["items"]); step=(sc["dur"]-0.8)/max(n,1)
        hs=[len(wrap(d,it,fnt("SemiBold",52),820))*68+60 for it in sc["items"]]
        tot=sum(hs)+34*(n-1); y=max(470,int((H-150-480-tot)/2+480))
        for i,it in enumerate(sc["items"]):
            t0=0.4+i*step*0.9; a=eb((t-t0)/0.5)
            f=fnt("SemiBold",52); lines=wrap(d,it,f,820); hh=len(lines)*68+60
            x0=60+(1-a)*(-900); d.rounded_rectangle((x0,y,x0+W-120,y+hh),radius=30,fill=NAVY2)
            d.ellipse((x0+34,y+hh/2-22,x0+78,y+hh/2+22),fill=ORANGE)
            d.text((x0+34+14 if False else x0+44,y+hh/2-22+2),str(i+1),font=fnt("ExtraBold",30),fill=NAVY) if False else None
            yy=y+30
            for l in lines: d.text((x0+110,yy),l,font=f,fill=OFF); yy+=68
            y+=hh+34
    elif ty=="stats":
        ctext(d,sc["title"].upper(),300,fnt("ExtraBold",78),ORANGE,eo(t/0.4),0)
        d.rectangle((W/2-80,400,W/2+80,408),fill=ORANGE); y=int(max(500,(H-150-480-(len(sc["stats"])*380-50))/2+480))
        for i,(big,lab) in enumerate(sc["stats"]):
            t0=0.35+i*0.55; a=eb((t-t0)/0.55); p=eo((t-t0)/0.9)
            d.rounded_rectangle((60,y,W-60,y+330),radius=36,fill=NAVY2)
            try: num=float(big.replace(" ","").replace(",",".")); isnum=True
            except: isnum=False
            if isnum:
                v=num*p; s=f"{v:,.0f}".replace(","," ") if num>=100 else (f"{v:.1f}".replace(".",",") if "," in big else f"{v:.0f}")
            else: s=big
            f=fnt("ExtraBold",150); sz=150
            while tw(d,s,f)>940 and sz>70: sz-=10; f=fnt("ExtraBold",sz)
            ctext(d,s,y+40+(1-a)*60,f,ORANGE,min(1,a*1.5))
            ctext(d,lab,y+230,fnt("SemiBold",46),OFF,min(1,a*1.5)); y+=380
    elif ty=="outro":
        a=eb(t/0.6); f=fnt("ExtraBold",110); y=640
        for i,l in enumerate(wrap(d,sc["title"],f,940)):
            ctext(d,l,y,f,OFF,min(1,a*1.4),(1-a)*80); y+=130
        ctext(d,sc.get("sub",""),y+30,fnt("Medium",50),ORANGE,eo((t-0.5)/0.5),0)
        pulse=1+0.04*math.sin(t*8); w=int(700*pulse); h=int(120*pulse)
        cy=1120; d.rounded_rectangle(((W-w)/2,cy,(W+w)/2,cy+h),radius=60,fill=ORANGE)
        ct=sc.get("cta","Abonne-toi ➜"); ct="ABONNE-TOI"; ff=fnt("ExtraBold",56)
        d.text(((W-tw(d,ct,ff))/2,cy+h/2-34),ct,font=ff,fill=NAVY)
scs=spec["scenes"]; HERE=os.path.dirname(os.path.abspath(__file__)); vo=[]
if any(s.get("voice") for s in scs):
    sys.path.insert(0,HERE); import make_voice
    for i,s in enumerate(scs):
        if s.get("voice"):
            f=f"{out}.v{i}.wav"; dv=make_voice.synth(s["voice"],f,spec.get("speed",1.0)); s["dur"]=max(s["dur"],dv+0.8); vo.append((i,f))
total=sum(s["dur"] for s in scs); N=int(total*FPS)
mus=out+".wav"
subprocess.run([sys.executable,"-I",os.path.join(HERE,"make_music.py"),mus,str(total+0.5),str(spec.get("bpm",108))],check=True)
if vo:
    import numpy as np, soundfile as sf
    m,sr=sf.read(mus); m=m if m.ndim==1 else m.mean(1); m=m*0.30; tr=m.copy()
    for i,f in vo:
        v,vsr=sf.read(f); st=int((sum(x["dur"] for x in scs[:i])+0.25)*sr)
        if vsr!=sr:
            v=np.interp(np.linspace(0,len(v)-1,int(len(v)*sr/vsr)),np.arange(len(v)),v)
        e=min(len(tr),st+len(v)); tr[st:e]+=v[:e-st]*1.0; os.remove(f)
    tr=np.clip(tr,-1,1); sf.write(mus,tr,sr)
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",mus,"-c:v","libx264","-preset","medium","-crf","23","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",out],stdin=subprocess.PIPE)
for fr in range(N):
    t=fr/FPS; acc=0
    for i,sc in enumerate(scs):
        if t<acc+sc["dur"] or i==len(scs)-1: lt=t-acc; break
        acc+=sc["dur"]
    img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img)
    bg(d,t,i); brand(d,t); scene(d,sc,lt,i); footer(d,t/total)
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait(); os.remove(mus)
