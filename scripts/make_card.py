# Usage: python3 -I make_card.py spec.json out.png
# spec: {"tag":"LE MOT DU JOUR","title":"Dividende","text":"phrase...","bullets":["..",".."],"source":"Source : ...","right":"17 octobre 2026"}
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
s=json.load(open(sys.argv[1])); W=H=1080
img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img)
header(d,W,s.get("right",""))
f=font("Bold",28); t=s.get("tag","")
if t:
    w=tw(d,t,f)+48; d.rounded_rectangle((60,150,60+w,206),radius=28,fill=ORANGE); d.text((84,160),t,font=f,fill=NAVY)
y=240; size=130
title=s["title"]
while size>56 and tw(d,title,font("ExtraBold",size))>960: size-=6
tl=wrap(d,title,font("ExtraBold",size),960)
for l in tl:
    d.text((60,y),l,font=font("ExtraBold",size),fill=OFF); y+=int(size*1.15)
y+=20
ft=font("Medium",42)
for l in wrap(d,s.get("text",""),ft,960): d.text((60,y),l,font=ft,fill=OFF); y+=58
y+=24
fb=font("SemiBold",36)
for b in s.get("bullets",[]):
    d.ellipse((60,y+12,84,y+36),fill=ORANGE)
    for i,l in enumerate(wrap(d,b,fb,880)):
        d.text((105,y),l,font=fb,fill=OFF); y+=50
    y+=12
footer(d,W,H,s.get("source",""))
img.convert("RGB").save(sys.argv[2])
