# Voix off française (Kokoro ONNX, gratuit, hors ligne). Usage: python3 -I make_voice.py "texte" out.wav [speed]
import sys,os,subprocess
D="/tmp/tts"; os.makedirs(D,exist_ok=True)
def ensure():
    try: import kokoro_onnx, soundfile
    except ImportError: subprocess.run([sys.executable,"-m","pip","install","--break-system-packages","-q","kokoro-onnx","soundfile"],check=True)
    for f in ("kokoro-v1.0.int8.onnx","voices-v1.0.bin"):
        p=f"{D}/{f}"
        if not os.path.exists(p) or os.path.getsize(p)<1e6:
            subprocess.run(["curl","-sL","-m","300","-o",p,f"https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/{f}"],check=True)
ACR={"SGI":"S G I","BRVM":"B R V M","UMOA":"U M O A","UEMOA":"U E M O A","FCFA":"francs C F A","BOC":"B O C","OAT":"O A T","BAT":"B A T","IRVM":"I R V M","PIB":"P I B","Mds":"milliards"}
def say_num(m):
    from num2words import num2words
    s=m.group(0).replace("\u202f","").replace(" ","").replace(",",".")
    try:
        v=float(s)
        if "." in s: ent,dec=s.split("."); return num2words(int(ent),lang="fr")+" virgule "+" ".join(num2words(int(c),lang="fr") if c!="0" else "zéro" for c in dec) if dec.startswith("0") else num2words(int(ent),lang="fr")+" virgule "+num2words(int(dec),lang="fr")
        return num2words(int(v),lang="fr")
    except Exception: return m.group(0)
def normalize(x):
    return x.replace("\u2212","moins ")
def chunks(text):
    import re
    out=[]
    for s in re.split(r"(?<=[.!?])\s+",text.strip()):
        if not s: continue
        if len(s.split())>20 and "," in s:
            parts=s.split(", "); cur=""
            for p in parts:
                cur=(cur+", "+p) if cur else p
                if len(cur.split())>=9: out.append(cur+","); cur=""
            if cur: out.append(cur)
        else: out.append(s)
    return out
def synth(text,out,speed=1.03):
    import numpy as np
    ensure()
    from kokoro_onnx import Kokoro; import soundfile as sf
    k=Kokoro(f"{D}/kokoro-v1.0.int8.onnx",f"{D}/voices-v1.0.bin")
    parts=chunks(text); segs=[]; sr=24000
    for x in parts:
        sp=speed
        a,sr=k.create(normalize(x),voice="ff_siwis",speed=sp,lang="fr-fr")
        a=np.trim_zeros(a.copy(),"fb") if False else a.copy()
        n=int(sr*0.02); a[:n]*=np.linspace(0,1,n); a[-n:]*=np.linspace(1,0,n)
        segs.append(a); gap=0.45 if x[-1] in ".!?" else (0.12 if x[-1]=="," else 0.3)
        segs.append(np.zeros(int(sr*gap)))
    raw=out+".raw.wav"; sf.write(raw,np.concatenate(segs[:-1]),sr)
    flt="highpass=f=90,equalizer=f=200:t=q:w=1:g=2.0,equalizer=f=3200:t=q:w=1:g=1.5,equalizer=f=6800:t=q:w=1.5:g=-3.5,acompressor=threshold=-21dB:ratio=2.2:attack=10:release=160,aecho=0.9:0.55:22:0.05,loudnorm=I=-16:TP=-1.5"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af",flt,"-ar","24000",out],check=True); os.remove(raw)
    import soundfile as sf2; d=sf2.info(out); return d.frames/d.samplerate
if __name__=="__main__": print(synth(sys.argv[1],sys.argv[2],float(sys.argv[3]) if len(sys.argv)>3 else 0.93))
