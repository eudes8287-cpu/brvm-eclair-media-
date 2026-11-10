#!/usr/bin/env python3
"""Synthèse — format « sujet unique » (45-65 s) : clips libres + voix Kokoro + musique + sous-titres karaoké.
Usage : python3 deep_dive.py spec.json out.mp4
Spec : {"lang","engine"(edge|kokoro),"edge_voice","rate","bpm","brand","segments":[{"shots":[{"clip"(mp4 ou jpg),"ss","fx","w"}] (ou clip/ss/fx),"voice","caption","num","title","big"}]}
 - clip : chemin du clip (Pixabay via Orshot, 1920x1080 ou 1354x720) ; ss : début dans le clip (s) ;
   fx : centre horizontal du cadrage vertical (0..1) ; num/title/big : habillage (facultatifs).
"""
import json, sys, os, subprocess, re
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
W, H, FPS = 1080, 1920, 30
GOLD = "&H003CB4F0"   # (240,180,60) en BGR
WHITE = "&H00FFFFFF"


def ts(t):
    cs = int(round(t * 100)); h = cs // 360000; m = cs // 6000 % 60; s = cs // 100 % 60; c = cs % 100
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def karaoke(text, vd):
    words = text.split(); tot = sum(len(w) for w in words) or 1
    out = []
    for w in words:
        cs = max(8, int(round(vd * 100 * len(w) / tot)))
        out.append("{\\k%d}%s" % (cs, w))
    return " ".join(out)


def tts_edge(text, wav, voice="fr-FR-VivienneMultilingualNeural", rate="+0%"):
    """Voix neuronale Microsoft (edge-tts) via le proxy de l'agent ; renvoie la durée, ou None si indisponible."""
    import asyncio, edge_tts, soundfile as sf
    mp3 = wav + ".mp3"
    async def go():
        c = edge_tts.Communicate(text, voice, rate=rate, proxy=os.environ.get("HTTPS_PROXY") or None)
        await c.save(mp3)
    for _ in range(3):
        try:
            asyncio.run(go())
            if os.path.getsize(mp3) > 2000:
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "24000", "-ac", "1", wav], check=True)
                d, r = sf.read(wav); return len(d) / r
        except Exception as e:
            print("edge-tts retry:", e)
    return None


def gradient(path):
    y = np.arange(H, dtype=np.float32)[:, None]
    top = np.clip(1 - y / 620, 0, 1) ** 1.4 * 0.70
    bot = np.clip((y - 1050) / 870, 0, 1) ** 1.3 * 0.78
    a = np.clip(top + bot, 0, 0.85)
    a = np.repeat(a, W, axis=1)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(path)


def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    lang = spec.get("lang", "fr")
    voice, vl = ("ff_siwis", "fr-fr") if lang == "fr" else (spec.get("voice", "af_heart"), "en-us")
    segs = spec["segments"]; tmp = out + ".work"; os.makedirs(tmp, exist_ok=True)
    from synthese_video import synth
    import soundfile as sf
    for i, s in enumerate(segs):
        f = f"{tmp}/v{i}.wav"
        vd = None
        if spec.get("engine", "edge") == "edge":
            vd = tts_edge(s["voice"], f, spec.get("edge_voice", "fr-FR-VivienneMultilingualNeural" if lang == "fr" else "en-US-AvaMultilingualNeural"), spec.get("rate", "+0%"))
        if vd is None:
            vd = synth(s["voice"], f, voice, vl, spec.get("speed", 0.97))
        s["vd"] = vd; s["vf"] = f
        s["dur"] = s["vd"] + 0.2 + (0.8 if i == len(segs) - 1 else 0.38)
    total = sum(s["dur"] for s in segs)

    # --- segments vidéo verticaux : plusieurs plans par fait (vidéo ou photo avec zoom lent)
    parts = []
    PHOTO = (".jpg", ".jpeg", ".png", ".webp")
    for i, s in enumerate(segs):
        shots = s.get("shots") or [{"clip": s["clip"], "ss": s.get("ss", 0), "fx": s.get("fx", 0.5)}]
        wts = [float(sh.get("w", 1)) for sh in shots]; tw = sum(wts)
        for k, sh in enumerate(shots):
            o = f"{tmp}/s{i}_{k}.mp4"
            d = s["dur"] * wts[k] / tw
            clip = sh["clip"]; fx = sh.get("fx", 0.5); sw0 = 1.0
            if clip.lower().endswith(PHOTO):
                im = Image.open(clip).convert("RGB"); iw, ih = im.size
                cw_ = min(iw, int(ih * 9 / 16)); x0 = max(0, min(iw - cw_, int(fx * iw - cw_ / 2)))
                im = im.crop((x0, 0, x0 + cw_, ih)).resize((1620, 2880), Image.LANCZOS)
                pf = f"{tmp}/p{i}_{k}.png"; im.save(pf)
                z0, z1 = (1.0, 1.22) if (i + k) % 2 == 0 else (1.22, 1.0)
                n = int(d * FPS) + 2
                vf = (f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={n}:s={W}x{H}:fps={FPS},"
                      f"trim=duration={d:.3f},setpts=PTS-STARTPTS,eq=contrast=1.06:saturation=1.1,format=yuv420p")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pf, "-an", "-vf", vf, "-c:v", "libx264",
                                "-preset", "veryfast", "-crf", "20", o], check=True)
            else:
                pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=width,height,duration", "-of", "json", clip], capture_output=True, text=True)
                st = json.loads(pr.stdout)["streams"][0]; cw, ch = int(st["width"]), int(st["height"])
                avail = max(0.5, float(st["duration"]) - sh.get("ss", 0))
                slow = max(1.0, min(1.35, d / avail))
                sh_ = 2100; sw = int(cw * sh_ / ch) // 2 * 2
                span = sw - W
                x0 = max(0, min(span, int(fx * sw - W / 2)))
                pan = 70 * (1 if (i + k) % 2 == 0 else -1)
                xe = f"max(0,min({span},{x0}+({pan})*t/{d:.2f}))"
                vf = (f"setpts={slow:.3f}*PTS,scale={sw}:{sh_},crop={W}:{H}:x='{xe}':y='({sh_}-{H})/2',"
                      f"fps={FPS},tpad=stop_mode=clone:stop_duration=2,trim=duration={d:.3f},setpts=PTS-STARTPTS,"
                      f"eq=contrast=1.06:saturation=1.12,format=yuv420p")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{sh.get('ss', 0)}", "-i", clip, "-an",
                                "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", o], check=True)
            parts.append(o)
    lst = f"{tmp}/list.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    cat = f"{tmp}/cat.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cat], check=True)

    # --- sous-titres / habillage ASS
    ev = [f"Dialogue: 1,{ts(0)},{ts(total)},Brand,,0,0,0,,SYNTHÈSE · {spec.get('brand', 'DÉCOUVERTE')}"]
    t0 = 0.0
    for i, s in enumerate(segs):
        a, b = t0, t0 + s["dur"]
        if s.get("title"):
            num = f"{{\\c{GOLD}&}}{s['num']}{{\\c{WHITE}&}}   " if s.get("num") else ""
            ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Title,,0,0,0,,{{\\fad(120,0)}}{num}{s['title']}")
        if s.get("big"):
            ev.append(f"Dialogue: 2,{ts(a + 0.15)},{ts(b)},Big,,0,0,0,,{{\\fad(120,0)\\fscx55\\fscy55\\t(0,260,\\fscx100\\fscy100)}}{s['big']}")
        cap = karaoke(s.get("caption", s["voice"]), s["vd"])
        ev.append(f"Dialogue: 3,{ts(a + 0.2)},{ts(b)},Cap,,0,0,0,,{cap}")
        t0 = b
    ev = [e for e in ev if e]
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Brand,Poppins,40,{GOLD},{GOLD},&H00000000,&H00000000,-1,0,0,0,100,100,4,0,1,3,0,8,60,60,120,1
Style: Title,Poppins,66,{WHITE},{WHITE},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,8,80,80,215,1
Style: Big,Poppins,150,{GOLD},{GOLD},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,8,60,60,420,1
Style: Cap,Poppins,58,{GOLD},{WHITE},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,95,155,385,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
""" + "\n".join(ev) + "\n"
    assf = f"{tmp}/o.ass"; open(assf, "w", encoding="utf-8").write(ass)
    grad = f"{tmp}/grad.png"; gradient(grad)

    # --- audio : musique + voix
    mus = f"{tmp}/m.wav"
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "..", "..", "scripts", "make_music.py"),
                    mus, str(total + 0.5), str(spec.get("bpm", 100))], check=True)
    m, sr = sf.read(mus); m = m if m.ndim == 1 else m.mean(1); tr = m * 0.20
    acc = 0.0
    for s in segs:
        v, vsr = sf.read(s["vf"]); st = int((acc + 0.2) * sr)
        if vsr != sr:
            v = np.interp(np.linspace(0, len(v) - 1, int(len(v) * sr / vsr)), np.arange(len(v)), v)
        e = min(len(tr), st + len(v)); tr[st:e] += v[:e - st]; acc += s["dur"]
    fa = 0.6; n = int(fa * sr); tr[-n:] *= np.linspace(1, 0, n)
    mix = f"{tmp}/mix.wav"; sf.write(mix, np.clip(tr, -1, 1), sr)

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cat, "-loop", "1", "-framerate", str(FPS), "-i", grad,
                    "-i", mix, "-filter_complex",
                    f"[0:v][1:v]overlay=shortest=1,subtitles={assf}:fontsdir=/usr/share/fonts/truetype/google-fonts[v];"
                    f"[2:a]loudnorm=I=-14:TP=-1.5:LRA=9[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-r", str(FPS), "-shortest", "-movflags", "+faststart", out], check=True)
    print("OK", out, round(total, 1), "s")


if __name__ == "__main__":
    main()
