from PIL import Image, ImageDraw, ImageFont
NAVY=(11,31,58); NAVY2=(20,46,82); ORANGE=(255,122,26); OFF=(245,241,232)
DISCLAIMER="Ceci est une information, pas un conseil en investissement"
GREEN=(34,197,94); RED=(239,68,68); MUTED=(150,168,196)
FD="/usr/share/fonts/opentype/inter/"
def font(w,s): return ImageFont.truetype(FD+f"Inter-{w}.otf",s)
def tw(d,t,f):
    b=d.textbbox((0,0),t,font=f); return b[2]-b[0]
def bolt(d,x,y,s,c):
    p=[(0.55,0),(0.05,0.58),(0.42,0.58),(0.30,1.0),(0.95,0.38),(0.55,0.38),(0.72,0)]
    d.polygon([(x+a*s,y+b*s) for a,b in p],fill=c)
def wrap(d,t,f,mw):
    out,cur=[],""
    for w in t.split():
        c=(cur+" "+w).strip()
        if tw(d,c,f)<=mw: cur=c
        else: out.append(cur); cur=w
    out.append(cur); return out
def header(d,W,right=""):
    bolt(d,60,38,56,ORANGE); d.text((128,40),"BRVM ÉCLAIR",font=font("ExtraBold",40),fill=OFF)
    if right:
        f=font("Medium",26); d.text((W-60-tw(d,right,f),50),right,font=f,fill=MUTED)
def footer(d,W,H,source=""):
    if source: d.text((60,H-85),source,font=font("Medium",22),fill=MUTED)
    f=font("Bold",20); t=DISCLAIMER
    d.text((W-60-tw(d,t,f),H-50),t,font=f,fill=ORANGE)
