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
def synth(text,out,speed=0.93):
    import re,numpy as np
    ensure()
    from kokoro_onnx import Kokoro; import soundfile as sf
    k=Kokoro(f"{D}/kokoro-v1.0.int8.onnx",f"{D}/voices-v1.0.bin")
    parts=[x.strip() for x in re.split(r"(?<=[.!?:])\s+",text) if x.strip()]; segs=[]; sr=24000
    for x in parts:
        a,sr=k.create(x,voice="ff_siwis",speed=speed,lang="fr-fr")
        n=int(sr*0.012); a=a.copy(); a[:n]*=np.linspace(0,1,n); a[-n:]*=np.linspace(1,0,n)
        segs.append(a); segs.append(np.zeros(int(sr*(0.38 if x[-1] in ".!?" else 0.2))))
    raw=out+".raw.wav"; sf.write(raw,np.concatenate(segs[:-1]),sr)
    # humanisation : chaleur, compression douce, légère ambiance de pièce
    flt="highpass=f=80,equalizer=f=180:t=q:w=1:g=2.5,equalizer=f=4500:t=q:w=1.2:g=-2.5,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,aecho=0.85:0.8:28|55:0.14|0.07,loudnorm=I=-16:TP=-1.5"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af",flt,"-ar","24000",out],check=True); os.remove(raw)
    import soundfile as sf2; d=sf2.info(out); return d.frames/d.samplerate
if __name__=="__main__": print(synth(sys.argv[1],sys.argv[2],float(sys.argv[3]) if len(sys.argv)>3 else 0.93))
