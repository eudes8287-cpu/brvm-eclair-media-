# Synthèse : vidéo verticale 1080x1920 (carte animée, chiffres, voix off, sous-titres, musique originale).
# Usage : python3 -I synthese_video.py spec.json out.mp4
# Sources libres : cartes Natural Earth (world-atlas, ISC), voix Kokoro (hors ligne), musique synthétisée.
import json, sys, os, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))  # make_voice (Kokoro) du dépôt
W, H, FPS = 1080, 1920, 30
BG = (8, 11, 22); PANEL = (16, 22, 40); GOLD = (240, 180, 60); CYAN = (70, 225, 215)
OFF = (244, 244, 240); MUTED = (140, 152, 180); LAND = (26, 38, 66); COAST = (58, 86, 138)
PX, PY, PW, PH = 60, 640, 960, 690          # panneau visuel
SS = 2                                       # sur-échantillonnage de la carte
FONT_DIR = "/usr/share/fonts/truetype/google-fonts/"
_F = {}


def F(w, s):
    k = (w, s)
    if k not in _F:
        _F[k] = ImageFont.truetype(FONT_DIR + f"Poppins-{w}.ttf", s)
    return _F[k]


_m = ImageDraw.Draw(Image.new("RGB", (4, 4)))


def tw(t, f):
    b = _m.textbbox((0, 0), t, font=f)
    return b[2] - b[0]


def wrap(t, f, mw):
    out, cur = [], ""
    for w in t.split():
        c = (cur + " " + w).strip()
        if tw(c, f) <= mw:
            cur = c
        else:
            out.append(cur); cur = w
    out.append(cur)
    return out


def clamp(x): return max(0.0, min(1.0, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def sm(x): x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10)
def eb(x):
    x = clamp(x); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def mixc(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------- voix ----------
def synth(text, out, voice="ff_siwis", lang="fr-fr", speed=0.95):
    import re, soundfile as sf
    import make_voice
    make_voice.ensure()
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{make_voice.D}/kokoro-v1.0.int8.onnx", f"{make_voice.D}/voices-v1.0.bin")
    parts = [x.strip() for x in re.split(r"(?<=[.!?:])\s+", text) if x.strip()]
    segs = []; sr = 24000
    for x in parts:
        a, sr = k.create(x, voice=voice, speed=speed, lang=lang)
        n = int(sr * 0.012); a = a.copy(); a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n)
        segs.append(a); segs.append(np.zeros(int(sr * (0.38 if x[-1] in ".!?" else 0.2))))
    raw = out + ".raw.wav"; sf.write(raw, np.concatenate(segs[:-1]), sr)
    flt = ("highpass=f=80,equalizer=f=180:t=q:w=1:g=2.5,equalizer=f=4500:t=q:w=1.2:g=-2.5,"
           "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,aecho=0.85:0.8:28|55:0.14|0.07,loudnorm=I=-16:TP=-1.5")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", flt, "-ar", "24000", out], check=True)
    os.remove(raw)
    d = sf.info(out); return d.frames / d.samplerate


# ---------- carte ----------
def merc(lat): return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def load_world(path):
    t = json.load(open(path)); sc = t["transform"]["scale"]; tr = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        a = np.cumsum(np.array(a, dtype=np.float64), axis=0)
        a[:, 0] = a[:, 0] * sc[0] + tr[0]; a[:, 1] = a[:, 1] * sc[1] + tr[1]; arcs.append(a)

    def ring(idx):
        parts = []
        for i in idx:
            p = arcs[i] if i >= 0 else arcs[~i][::-1]
            parts.append(p if not parts else p[1:])
        return np.vstack(parts)
    out = []
    for g in t["objects"]["countries"]["geometries"]:
        name = g.get("properties", {}).get("name", "")
        if name == "Antarctica":
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else ([g["arcs"]] if g["type"] == "Polygon" else [])
        for poly in polys:
            r = ring(poly[0])
            X = np.radians(r[:, 0]); Y = np.log(np.tan(np.pi / 4 + np.radians(np.clip(r[:, 1], -80, 84)) / 2))
            out.append((name, X, Y, X.min(), X.max(), Y.min(), Y.max()))
    return out


VAT = (41.9029, 12.4534)


def render_map(world, S, clon, clat, tt, hl, mk):
    w, h = PW * SS, PH * SS
    img = Image.new("RGB", (w, h), (10, 16, 32)); d = ImageDraw.Draw(img)
    cx = math.radians(clon); cy = merc(clat); s = S * SS
    x0, x1, y0, y1 = cx - w / 2 / s, cx + w / 2 / s, cy - h / 2 / s, cy + h / 2 / s
    for name, X, Y, a, b, c, e in world:
        if b < x0 or a > x1 or e < y0 or c > y1:
            continue
        if (b - a) * s < 1.5 and (e - c) * s < 1.5:
            continue
        pts = list(zip(((X - cx) * s + w / 2).tolist(), ((cy - Y) * s + h / 2).tolist()))
        it = name == "Italy"
        fill = mixc(LAND, (88, 70, 26), hl) if it else LAND
        line = mixc(COAST, GOLD, hl) if it else COAST
        d.polygon(pts, fill=fill)
        d.line(pts + [pts[0]], fill=line, width=3 if it and hl > 0.3 else 2)
    if hl > 0.2:
        lx = (math.radians(12.4) - cx) * s + w / 2; ly = (cy - merc(44.6)) * s + h / 2
        t = "ITALIE"; f = F("Bold", 30 * SS)
        d.text((lx - tw(t, f) / 2, ly), t, font=f, fill=mixc((10, 16, 32), (190, 170, 120), hl))
    if mk > 0:
        mx = (math.radians(VAT[1]) - cx) * s + w / 2; my = (cy - merc(VAT[0])) * s + h / 2
        ph = (tt * 0.9) % 1.0
        for k in (0.0, 0.5):
            p = (ph + k) % 1.0; r = (14 + 70 * p) * SS
            d.ellipse((mx - r, my - r, mx + r, my + r), outline=mixc((10, 16, 32), CYAN, (1 - p) * mk), width=4)
        r = 10 * SS
        d.ellipse((mx - r - 3, my - r - 3, mx + r + 3, my + r + 3), fill=(10, 16, 32))
        d.ellipse((mx - r, my - r, mx + r, my + r), fill=mixc((10, 16, 32), GOLD, mk))
        t = "Cité du Vatican"; f = F("Bold", 34 * SS); tx = mx + 55 * SS; ty = my - 110 * SS
        tx = min(tx, w - tw(t, f) - 30 * SS)
        d.line((mx + r * 0.7, my - r * 0.7, tx - 8, ty + 30 * SS), fill=mixc((10, 16, 32), GOLD, mk), width=3)
        d.text((tx, ty), t, font=f, fill=mixc((10, 16, 32), OFF, mk))
    return img.resize((PW, PH), Image.LANCZOS)


# ---------- éléments d'image ----------
def brand(d, cat):
    d.text((70, 168), "SYNTHÈSE", font=F("Bold", 42), fill=GOLD)
    f = F("Bold", 26); w = tw(cat, f) + 44
    d.rounded_rectangle((W - 70 - w, 168, W - 70, 218), radius=25, outline=CYAN, width=3)
    d.text((W - 70 - w + 22, 175), cat, font=f, fill=CYAN)


def title(d, txt, t, y0=272):
    size = 88; f = F("Bold", size); lines = wrap(txt, f, 940)
    while len(lines) > 3 and size > 60:
        size -= 6; f = F("Bold", size); lines = wrap(txt, f, 940)
    y = 260 + (360 - len(lines) * int(size * 1.2)) / 2   # centré dans la zone titre
    for i, l in enumerate(lines):
        a = eo((t - i * 0.1) / 0.35)
        col = GOLD if (i == len(lines) - 1) else OFF
        d.text(((W - tw(l, f)) / 2, y + (1 - a) * 40), l, font=f, fill=col)
        y += int(size * 1.2)


def captions(d, text, t, v0, vd):
    f = F("Bold", 56); words = text.split()
    wt = [len(w) + 1 for w in words]; tot = sum(wt); cum = 0; ts = []
    for x in wt:
        ts.append(v0 + vd * cum / tot); cum += x
    lines, cur = [], []
    for w in words:
        if tw(" ".join(cur + [w]), f) <= 940 or not cur:
            cur.append(w)
        else:
            lines.append(cur); cur = [w]
    lines.append(cur)
    y = 1375; i = 0; sp = tw(" ", f)
    for ln in lines:
        wd = [tw(w, f) for w in ln]; x = (W - (sum(wd) + sp * (len(ln) - 1))) / 2
        for w, ww in zip(ln, wd):
            nxt = ts[i + 1] if i + 1 < len(ts) else 1e9
            col = GOLD if ts[i] <= t < nxt else (OFF if t >= nxt else (120, 130, 155))
            d.text((x, y), w, font=f, fill=col); x += ww + sp; i += 1
        y += 76


def pitch(d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), radius=6, fill=(28, 130, 70), outline=OFF, width=2)
    d.line((x + w / 2, y, x + w / 2, y + h), fill=OFF, width=2)
    r = h * 0.22; d.ellipse((x + w / 2 - r, y + h / 2 - r, x + w / 2 + r, y + h / 2 + r), outline=OFF, width=2)


def visual(world, sc, t, k, durs, pn):
    """Dessine le panneau visuel. Retourne une image PW x PH."""
    ty = sc["type"]
    if ty in ("hook", "reveal"):
        if ty == "hook":
            u = t / max(durs[0], 0.1); S = 520 + 130 * u; clon, clat, hl, mk = 15 - 2 * u, 36 - 1 * u, 0.0, 0.0
        else:
            p = sm(t / 2.2); S = math.exp(math.log(650) + (math.log(7000) - math.log(650)) * p)
            clon = 13 + (12.6 - 13) * p; clat = 35 + (42.3 - 35) * p
            hl = sm((p - 0.35) / 0.55); mk = sm((p - 0.8) / 0.2)
        img = render_map(world, S, clon, clat, t, hl, mk)
        if ty == "hook":
            m = Image.new("L", (PW, PH), 0); md = ImageDraw.Draw(m)
            sz = int(380 * (1 + 0.05 * math.sin(t * 5))); f = F("Bold", sz)
            md.text(((PW - tw("?", f)) / 2, PH / 2 - sz * 0.72), "?", font=f, fill=215)
            img.paste(GOLD, (0, 0), m)
        return img
    img = Image.new("RGB", (PW, PH), PANEL); d = ImageDraw.Draw(img)
    if ty == "stat":
        p = eo(t / 1.3); v = sc["value"] * p
        s = f"{v:.2f}".replace(".", ","); f = F("Bold", 280)
        d.text(((PW - tw(s, f)) / 2, 90), s, font=f, fill=GOLD)
        u = sc.get("unit", ""); fu = F("Bold", 110)
        d.text(((PW - tw(u, fu)) / 2, 425), u, font=fu, fill=CYAN)
        a = eo((t - 1.5) / 0.5)
        if sc.get("sub"):
            fs = F("Medium", 58); c = mixc(PANEL, OFF, a)
            d.text(((PW - tw(sc["sub"], fs)) / 2, 595 + (1 - a) * 30), sc["sub"], font=fs, fill=c)
    elif ty == "compare":
        fb = F("Bold", 190); big = sc["big"]
        a = eb(t / 0.5)
        d.text(((PW - tw(big, fb)) / 2, 20 + (1 - a) * 40), big, font=fb, fill=GOLD)
        fl = F("Medium", 52); d.text(((PW - tw(sc["label"], fl)) / 2, 255), sc["label"], font=fl, fill=OFF)
        n = sc["count"]; cols = 10; w, h, gx, gy = 78, 42, 10, 9
        x0 = (PW - (cols * w + (cols - 1) * gx)) / 2
        for i in range(n):
            ta = 0.4 + i * (2.2 / n); pa = eb((t - ta) / 0.35)
            if pa <= 0:
                continue
            r, c = divmod(i, cols); cxp = x0 + c * (w + gx); cyp = 340 + r * (h + gy)
            sc_ = clamp(pa); ww, hh = w * sc_, h * sc_
            pitch(d, cxp + (w - ww) / 2, cyp + (h - hh) / 2, ww, hh)
    elif ty == "outro":
        f = F("Bold", 150); s = "SYNTHÈSE"
        while tw(s, f) > 880:
            f = F("Bold", f.size - 8)
        a = eb(t / 0.6)
        d.text(((PW - tw(s, f)) / 2, 120 + (1 - a) * 50), s, font=f, fill=GOLD)
        t2 = sc.get("tag", "1 fait surprenant par jour"); f2 = F("Medium", 50)
        d.text(((PW - tw(t2, f2)) / 2, 330), t2, font=f2, fill=OFF)
        pulse = 1 + 0.05 * math.sin(t * 7); bw, bh = int(560 * pulse), int(130 * pulse)
        bx, by = (PW - bw) // 2, 470
        d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=bh // 2, fill=GOLD)
        lab = sc.get("cta", "SUIVRE"); fb2 = F("Bold", 64)
        d.text(((PW - tw(lab, fb2)) / 2, by + bh / 2 - 48), lab, font=fb2, fill=BG)
    return img


def make_bg():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
    g = np.clip(1 - r * 1.4, 0, 1)[..., None]
    base = np.array(BG, dtype=np.float32); hi = np.array((18, 26, 52), dtype=np.float32)
    return Image.fromarray((base + (hi - base) * g).astype(np.uint8))


def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    lang = spec.get("lang", "fr")
    voice, vl = ("ff_siwis", "fr-fr") if lang == "fr" else (spec.get("voice", "af_heart"), "en-us")
    world = load_world(os.path.join(HERE, "..", "data", "countries-50m.json"))
    scs = spec["scenes"]; vo = []
    for i, s in enumerate(scs):
        f = f"{out}.v{i}.wav"
        dv = synth(s["voice"], f, voice, vl, spec.get("speed", 0.95))
        s["vd"] = dv; s["dur"] = dv + 0.25 + (0.7 if i == len(scs) - 1 else 0.45)
        if s["type"] == "reveal":
            s["dur"] = max(s["dur"], 3.0)
        vo.append((i, f))
    total = sum(s["dur"] for s in scs); N = int(total * FPS)
    mus = out + ".wav"
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "..", "..", "scripts", "make_music.py"),
                    mus, str(total + 0.5), str(spec.get("bpm", 100))], check=True)
    import soundfile as sf
    m, sr = sf.read(mus); m = m if m.ndim == 1 else m.mean(1); tr = m * 0.20
    for i, f in vo:
        v, vsr = sf.read(f); st = int((sum(x["dur"] for x in scs[:i]) + 0.25) * sr)
        if vsr != sr:
            v = np.interp(np.linspace(0, len(v) - 1, int(len(v) * sr / vsr)), np.arange(len(v)), v)
        e = min(len(tr), st + len(v)); tr[st:e] += v[:e - st]; os.remove(f)
    sf.write(mus, np.clip(tr, -1, 1), sr)
    bg = make_bg(); mask = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PW - 1, PH - 1), radius=36, fill=255)
    durs = [s["dur"] for s in scs]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", mus, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    covers = {}
    for fr in range(N):
        t = fr / FPS; acc = 0
        for i, sc in enumerate(scs):
            if t < acc + sc["dur"] or i == len(scs) - 1:
                lt = t - acc; break
            acc += sc["dur"]
        img = bg.copy(); d = ImageDraw.Draw(img)
        brand(d, spec.get("category", "DÉCOUVERTE"))
        title(d, sc["title"], lt)
        vis = visual(world, sc, lt, i, durs, i)
        img.paste(vis, (PX, PY), mask)
        d.rounded_rectangle((PX, PY, PX + PW, PY + PH), radius=36, outline=(40, 54, 92), width=3)
        captions(d, sc.get("caption", sc["voice"]), lt, 0.25, sc["vd"])
        if fr in (2, int(N * 0.25), int(N * 0.5), int(N * 0.75), N - 8):
            img.save(f"{out}.f{fr}.png")
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait(); os.remove(mus)
    print("OK", out, round(total, 1), "s")


if __name__ == "__main__":
    main()
