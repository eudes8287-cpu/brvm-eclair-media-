# Usage: python3 -I make_cloture.py data.json out.png
# data: {"date":"vendredi 16 octobre 2026","composite":{"v":"546,86","var":"-0,28 %","ytd":"+58,17 % depuis janvier"},
#  "b30":{"v":"264,57","var":"-0,39 %"},"prestige":{"v":"203,08","var":"-0,26 %"},
#  "stats":[["Capitalisation actions","21 445 Mds FCFA"],["Valeur échangée","2,92 Mds FCFA"],["Volume","865 675 titres"]],
#  "breadth":[13,25,8],"ups":[["NOM","cours","+4,75 %"],..3],"downs":[..3],"source":"Source : BOC BRVM du 16/10/2026"}
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
D=json.load(open(sys.argv[1])); W=H=1080
img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img)
header(d,W,D["date"])
d.text((60,125),"CLÔTURE BRVM",font=font("ExtraBold",66),fill=OFF); d.rectangle((60,205,200,211),fill=ORANGE)
def col(v): return RED if v.strip().startswith("-") else GREEN
c=D["composite"]
d.rounded_rectangle((60,235,1020,415),radius=28,fill=NAVY2)
d.text((95,260),"BRVM COMPOSITE",font=font("SemiBold",26),fill=ORANGE)
d.text((95,300),c["v"],font=font("ExtraBold",100),fill=OFF)
f=font("Bold",38); w=tw(d,c["var"],f)+44
d.rounded_rectangle((560,310,560+w,364),radius=27,fill=col(c["var"])); d.text((582,319),c["var"],font=f,fill=(255,255,255))
if c.get("ytd"): d.text((560,378),c["ytd"],font=font("Medium",22),fill=MUTED)
for x,lab,k in ((60,"BRVM 30","b30"),(550,"BRVM PRESTIGE","prestige")):
    e=D[k]; d.rounded_rectangle((x,435,x+470,525),radius=22,fill=NAVY2)
    d.text((x+28,450),lab,font=font("SemiBold",21),fill=ORANGE); d.text((x+28,478),e["v"],font=font("Bold",34),fill=OFF)
    fv=font("Bold",30); d.text((x+470-28-tw(d,e["var"],fv),484),e["var"],font=fv,fill=col(e["var"]))
x=60
for lab,val in D["stats"]:
    d.rounded_rectangle((x,545,x+305,625),radius=18,fill=NAVY2)
    d.text((x+20,555),lab,font=font("Medium",19),fill=MUTED); d.text((x+20,583),val,font=font("Bold",26),fill=OFF); x+=327
b=D["breadth"]
d.text((60,645),f"{b[0]} hausses",font=font("Bold",28),fill=GREEN); d.text((290,645),f"{b[1]} baisses",font=font("Bold",28),fill=RED); d.text((510,645),f"{b[2]} inchangés",font=font("Bold",28),fill=MUTED)
for x,title,rows,cc in ((60,"PLUS FORTES HAUSSES",D["ups"],GREEN),(550,"PLUS FORTES BAISSES",D["downs"],RED)):
    d.rounded_rectangle((x,700,x+470,960),radius=22,fill=NAVY2); d.rectangle((x,700,x+470,708),fill=cc)
    d.text((x+28,722),title,font=font("Bold",24),fill=cc); y=775
    for n,cours,v in rows:
        d.text((x+28,y),n,font=font("SemiBold",23),fill=OFF); d.text((x+28,y+30),cours+" FCFA",font=font("Regular",20),fill=MUTED)
        fv=font("ExtraBold",30); d.text((x+470-28-tw(d,v,fv),y+6),v,font=fv,fill=cc); y+=60
d.text((60,995),D.get("source",""),font=font("Medium",20),fill=MUTED)
f=font("Bold",20); t=DISCLAIMER; d.text((W-60-tw(d,t,f),995),t,font=f,fill=ORANGE)
img.save(sys.argv[2])
