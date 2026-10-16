# Usage: python3 -I make_card.py spec.json out.png
# spec: {"theme":"navy|orange|light|teal","layout":"standard|bignumber|qa",
#  "tag":"LE MOT DU JOUR","title":"Dividende","text":"définition en une phrase","bullets":["..",".."],
#  "clair":"En clair : explication très simple pour un débutant","retenir":"À retenir : ...",
#  "number":"209 FCFA","label":"par action (brut)",  # layout bignumber
#  "q":"Question ?","a":"Réponse",                    # layout qa
#  "source":"Source : ...","right":"17 octobre 2026"}
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
THEMES={"navy":dict(bg=NAVY,fg=OFF,acc=ORANGE,card=NAVY2,mut=MUTED,on_acc=NAVY),
"orange":dict(bg=ORANGE,fg=NAVY,acc=NAVY,card=(255,150,70),mut=(120,60,10),on_acc=OFF),
"light":dict(bg=OFF,fg=NAVY,acc=ORANGE,card=(255,255,255),mut=(96,112,140),on_acc=NAVY),
"teal":dict(bg=(8,60,66),fg=OFF,acc=(250,204,21),card=(14,84,92),mut=(150,200,205),on_acc=(8,60,66))}
s=json.load(open(sys.argv[1])); W=H=1080
T=THEMES[s.get("theme","navy")]; img=Image.new("RGB",(W,H),T["bg"]); d=ImageDraw.Draw(img)
bolt(d,60,38,56,T["acc"] if s.get("theme") != "orange" else NAVY); d.text((128,40),"BRVM ÉCLAIR",font=font("ExtraBold",40),fill=T["fg"])
if s.get("right"):
    f=font("Medium",26); d.text((W-60-tw(d,s["right"],f),50),s["right"],font=f,fill=T["mut"])
def tag(y):
    t=s.get("tag","")
    if t:
        f=font("Bold",28); w=tw(d,t,f)+48; d.rounded_rectangle((60,y,60+w,y+56),radius=28,fill=T["acc"]); d.text((84,y+10),t,font=f,fill=T["on_acc"])
def box(y,label,text,size=34):
    f=font("SemiBold",size); lines=wrap(d,text,f,880); h=len(lines)*(size+14)+70
    d.rounded_rectangle((60,y,W-60,y+h),radius=26,fill=T["card"]); d.text((90,y+18),label,font=font("ExtraBold",24),fill=T["acc"])
    yy=y+56
    for l in lines: d.text((90,yy),l,font=f,fill=T["fg"]); yy+=size+14
    return y+h+20
lay=s.get("layout","standard"); tag(150); y=240
title=s.get("title","")
if lay=="bignumber":
    size=170; f=font("ExtraBold",size)
    while tw(d,s["number"],f)>960 and size>70: size-=10; f=font("ExtraBold",size)
    d.text((60,y),s["number"],font=f,fill=T["acc"]); y+=int(size*1.2)
    for l in wrap(d,s.get("label",""),font("Bold",46),960): d.text((60,y),l,font=font("Bold",46),fill=T["fg"]); y+=60
    y+=20
    for l in wrap(d,title,font("ExtraBold",56),960): d.text((60,y),l,font=font("ExtraBold",56),fill=T["fg"]); y+=70
elif lay=="qa":
    f=font("ExtraBold",76)
    for l in wrap(d,s["q"],f,960): d.text((60,y),l,font=f,fill=T["fg"]); y+=94
    y+=20; d.rounded_rectangle((60,y,W-60,y+8),radius=4,fill=T["acc"]); y+=40
    for l in wrap(d,s["a"],font("Medium",44),960): d.text((60,y),l,font=font("Medium",44),fill=T["fg"]); y+=60
else:
    size=130
    while size>56 and tw(d,title,font("ExtraBold",size))>960: size-=6
    for l in wrap(d,title,font("ExtraBold",size),960): d.text((60,y),l,font=font("ExtraBold",size),fill=T["fg"]); y+=int(size*1.15)
y+=14
if s.get("text") and lay!="qa":
    for l in wrap(d,s["text"],font("Medium",40),960): d.text((60,y),l,font=font("Medium",40),fill=T["fg"]); y+=54
    y+=16
fb=font("SemiBold",34)
for b in s.get("bullets",[]):
    d.ellipse((60,y+10,82,y+32),fill=T["acc"])
    for l in wrap(d,b,fb,880): d.text((100,y),l,font=fb,fill=T["fg"]); y+=46
    y+=10
y+=10
if s.get("clair"): y=box(y,"EN CLAIR",s["clair"])
if s.get("retenir"): y=box(y,"À RETENIR",s["retenir"])
if s.get("source"): d.text((60,H-85),s["source"],font=font("Medium",22),fill=T["mut"])
f=font("Bold",20); t="Information, pas un conseil en investissement"
d.text((W-60-tw(d,t,f),H-50),t,font=f,fill=T["acc"] if s.get("theme")!="orange" else NAVY)
img.save(sys.argv[2])
