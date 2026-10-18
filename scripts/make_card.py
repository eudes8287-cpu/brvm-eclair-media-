# Usage: python3 -I make_card.py spec.json out.png
# CHARTE (points de repère fixes) : éclair + « BRVM ÉCLAIR » en haut à gauche, police Inter, accent orange/jaune,
#   pastille de rubrique, blocs « EN CLAIR » / « À RETENIR », mention légale en bas à droite.
# VARIABLE : theme, layout, format, deco.
# spec: {"theme":"navy|orange|light|teal|sand|violet|emerald|wine","layout":"standard|bignumber|qa|steps|versus|poster",
#  "format":"square|portrait","deco":"bolt|rings|dots|diag|none","tag":"..","title":"..","text":"..","bullets":[..],
#  "clair":"..","retenir":"..","number":"..","label":"..","q":"..","a":"..","source":"..","right":"(date: seulement pour les clôtures)",
#  "a_title","a_text","b_title","b_text"  # versus
# }
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
THEMES={"navy":dict(bg=NAVY,fg=OFF,acc=ORANGE,card=NAVY2,mut=MUTED,on_acc=NAVY),
"orange":dict(bg=ORANGE,fg=NAVY,acc=NAVY,card=(255,150,70),mut=(120,60,10),on_acc=OFF),
"light":dict(bg=OFF,fg=NAVY,acc=ORANGE,card=(255,255,255),mut=(96,112,140),on_acc=NAVY),
"teal":dict(bg=(8,60,66),fg=OFF,acc=(250,204,21),card=(14,84,92),mut=(150,200,205),on_acc=(8,60,66)),
"sand":dict(bg=(244,232,208),fg=NAVY,acc=ORANGE,card=(255,250,240),mut=(120,104,80),on_acc=NAVY),
"violet":dict(bg=(38,26,92),fg=OFF,acc=ORANGE,card=(58,42,126),mut=(176,166,222),on_acc=NAVY),
"emerald":dict(bg=(6,62,46),fg=OFF,acc=(255,184,40),card=(12,88,66),mut=(150,208,186),on_acc=(6,62,46)),
"wine":dict(bg=(82,22,44),fg=OFF,acc=ORANGE,card=(110,36,64),mut=(222,170,186),on_acc=NAVY)}
s=json.load(open(sys.argv[1])); W=1080; H=1350 if s.get("format")=="portrait" else 1080
T=THEMES[s.get("theme","navy")]; img=Image.new("RGB",(W,H),T["bg"]); d=ImageDraw.Draw(img)
def mix(a,b,k): return tuple(int(a[i]+(b[i]-a[i])*k) for i in range(3))
DC=mix(T["bg"],T["fg"],0.07)
deco=s.get("deco","bolt"); lay=s.get("layout","standard")
if deco=="bolt": bolt(d,W-520,H-720,720,DC)
elif deco=="rings":
    for i,r in enumerate((260,420,580)): d.ellipse((W-r+120,H-r+120,W+r+120,H+r+120),outline=DC,width=8)
elif deco=="dots":
    for gx in range(8):
        for gy in range(8): d.ellipse((60+gx*38,H-300+gy*38,76+gx*38,H-284+gy*38),fill=DC)
elif deco=="diag":
    d.polygon([(W,0),(W,520),(W-520,0)],fill=DC); d.polygon([(0,H),(0,H-260),(260,H)],fill=DC)
acc_logo=T["acc"] if s.get("theme")!="orange" else NAVY
bolt(d,60,38,56,acc_logo); d.text((128,40),"BRVM ÉCLAIR",font=font("ExtraBold",40),fill=T["fg"])
if s.get("right"):
    f=font("Medium",26); d.text((W-60-tw(d,s["right"],f),50),s["right"],font=f,fill=T["mut"])
def tag(y,cx=False):
    t=s.get("tag","")
    if t:
        f=font("Bold",28); w=tw(d,t,f)+48; x=(W-w)//2 if cx else 60
        d.rounded_rectangle((x,y,x+w,y+56),radius=28,fill=T["acc"]); d.text((x+24,y+10),t,font=f,fill=T["on_acc"])
def box(y,label,text,size=34):
    f=font("SemiBold",size); lines=wrap(d,text,f,880); h=len(lines)*(size+14)+70
    d.rounded_rectangle((60,y,W-60,y+h),radius=26,fill=T["card"]); d.text((90,y+18),label,font=font("ExtraBold",24),fill=T["acc"])
    yy=y+56
    for l in lines: d.text((90,yy),l,font=f,fill=T["fg"]); yy+=size+14
    return y+h+20
def title_block(y,maxsz=130,center=False):
    title=s.get("title",""); size=maxsz
    while size>56 and tw(d,title,font("ExtraBold",size))>960: size-=6
    for l in wrap(d,title,font("ExtraBold",size),960):
        x=(W-tw(d,l,font("ExtraBold",size)))//2 if center else 60
        d.text((x,y),l,font=font("ExtraBold",size),fill=T["fg"]); y+=int(size*1.15)
    return y
tag(150,cx=(lay=="poster")); y=240
if lay=="bignumber":
    size=170; f=font("ExtraBold",size)
    while tw(d,s["number"],f)>960 and size>70: size-=10; f=font("ExtraBold",size)
    d.text((60,y),s["number"],font=f,fill=T["acc"]); y+=int(size*1.2)
    for l in wrap(d,s.get("label",""),font("Bold",46),960): d.text((60,y),l,font=font("Bold",46),fill=T["fg"]); y+=60
    y+=20
    for l in wrap(d,s.get("title",""),font("ExtraBold",56),960): d.text((60,y),l,font=font("ExtraBold",56),fill=T["fg"]); y+=70
elif lay=="qa":
    f=font("ExtraBold",76)
    for l in wrap(d,s["q"],f,960): d.text((60,y),l,font=f,fill=T["fg"]); y+=94
    y+=20; d.rounded_rectangle((60,y,W-60,y+8),radius=4,fill=T["acc"]); y+=40
    for l in wrap(d,s["a"],font("Medium",44),960): d.text((60,y),l,font=font("Medium",44),fill=T["fg"]); y+=60
elif lay=="poster":
    y=max(y+60,int(H*0.27)); y=title_block(y,150,center=True)+20
    if s.get("text"):
        for l in wrap(d,s["text"],font("Medium",44),900):
            d.text(((W-tw(d,l,font("Medium",44)))//2,y),l,font=font("Medium",44),fill=T["fg"]); y+=60
    y+=30
elif lay=="steps":
    y=title_block(y,96)+30; fb=font("SemiBold",40)
    for i,b in enumerate(s.get("bullets",[])):
        lines=wrap(d,b,fb,780); h=max(110,len(lines)*52+40)
        d.rounded_rectangle((60,y,W-60,y+h),radius=26,fill=T["card"])
        d.ellipse((84,y+h//2-36,156,y+h//2+36),fill=T["acc"]); f2=font("ExtraBold",44); n=str(i+1)
        d.text((120-tw(d,n,f2)//2,y+h//2-30),n,font=f2,fill=T["on_acc"])
        yy=y+(h-len(lines)*52)//2
        for l in lines: d.text((184,yy),l,font=fb,fill=T["fg"]); yy+=52
        y+=h+22
    y+=6
elif lay=="versus":
    y=title_block(y,90)+26; cw=(W-120-30)//2
    for k,(tt,tx) in enumerate(((s["a_title"],s["a_text"]),(s["b_title"],s["b_text"]))):
        x=60+k*(cw+30); fa=font("ExtraBold",46); ft=font("Medium",34)
        tl=wrap(d,tt,fa,cw-50); xl=wrap(d,tx,ft,cw-50); h=len(tl)*58+len(xl)*46+70
        h=max(h,300); d.rounded_rectangle((x,y,x+cw,y+h),radius=28,fill=T["card"]); d.rectangle((x,y,x+cw,y+10),fill=T["acc"])
        yy=y+34
        for l in tl: d.text((x+25,yy),l,font=fa,fill=T["acc"]); yy+=58
        yy+=10
        for l in xl: d.text((x+25,yy),l,font=ft,fill=T["fg"]); yy+=46
    y+=h+30
else:
    y=title_block(y,130)
y+=14
if s.get("text") and lay not in ("qa","poster"):
    for l in wrap(d,s["text"],font("Medium",40),960): d.text((60,y),l,font=font("Medium",40),fill=T["fg"]); y+=54
    y+=16
fb=font("SemiBold",34)
if lay not in ("steps",):
    for b in s.get("bullets",[]):
        d.ellipse((60,y+10,82,y+32),fill=T["acc"])
        for l in wrap(d,b,fb,880): d.text((100,y),l,font=fb,fill=T["fg"]); y+=46
        y+=10
y+=10
if s.get("clair"): y=box(y,"EN CLAIR",s["clair"])
if s.get("retenir"): y=box(y,"À RETENIR",s["retenir"])
assert y<=H-70, f"débordement: contenu jusqu'à y={y} (limite {H-70})"
if s.get("source"): d.text((60,H-85),s["source"],font=font("Medium",22),fill=T["mut"])
f=font("Bold",20); t=DISCLAIMER
d.text((W-60-tw(d,t,f),H-50),t,font=f,fill=T["acc"] if s.get("theme")!="orange" else NAVY)
img.save(sys.argv[2])
