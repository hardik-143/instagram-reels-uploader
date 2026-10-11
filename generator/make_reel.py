#!/usr/bin/env python3
"""What if animals could talk for just one day? — 9:16 animated Reel generator.
Renders frames with Pillow, synthesizes music + SFX with numpy, muxes with ffmpeg."""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
TOTAL = 56.0
HERE = os.path.dirname(os.path.abspath(__file__))

def pick(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise SystemExit("no font")

F_CAP = pick("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")
F_TITLE = pick("/usr/share/fonts/opentype/inter/Inter-Black.otf",
               "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
               "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", F_CAP)

OUTL = (38, 26, 48)
YEL = (255, 214, 10)
WHITE = (255, 255, 255)
RED = (225, 45, 75)
CPS = 0.05  # seconds per typed character

_fonts = {}
def font(size, path=F_CAP):
    k = (size, path)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def comp(frame, spr, x, y):
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    dx, dy = max(0, x), max(0, y)
    w = min(spr.width - sx, W - dx); h = min(spr.height - sy, H - dy)
    if w <= 0 or h <= 0:
        return
    if sx or sy or w < spr.width or h < spr.height:
        spr = spr.crop((sx, sy, sx + w, sy + h))
    frame.alpha_composite(spr, (dx, dy))

def paste_c(frame, spr, cx, cy, scale=1.0):
    if scale <= 0.02:
        return
    if abs(scale - 1) > 0.01:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    comp(frame, spr, cx - spr.width / 2, cy - spr.height / 2)

def wrap_words(words, f, maxw):
    lines, cur = [], []
    for w in words:
        if cur and f.getlength(" ".join(cur + [w])) > maxw:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines

def is_emph(w):
    s = w.strip(".,!?'\"")
    return len(s) > 1 and s.isalpha() and s.isupper()

# ---------------------------------------------------------------- characters
def draw_animal(kind, B, T, talk=0.0, blink=False, look=(0, 0), wink=False):
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))

    def E(b, fill, w=2.6, outline=OUTL):
        x0, y0, x1, y1 = b
        d.ellipse([x0 * u, y0 * u, x1 * u, y1 * u], fill=fill,
                  outline=outline if w else None, width=lw(w) if w else 0)

    def PG(pts, fill, w=2.6):
        d.polygon([(x * u, y * u) for x, y in pts], fill=fill,
                  outline=OUTL if w else None, width=lw(w) if w else 0)

    def LN(pts, w=2.0, fill=OUTL):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")

    def eyes(lx, rx, y, r, iris=None, slit=False, lid=None):
        for i, x in enumerate((lx, rx)):
            if blink or (wink and i == 1):
                d.arc([(x - r) * u, (y - r * 0.7) * u, (x + r) * u, (y + r * 0.7) * u],
                      200, 340, fill=OUTL, width=lw(3.2))
                continue
            E((x - r, y - r * 1.12, x + r, y + r * 1.12), (255, 255, 255))
            px, py = x + look[0] * r * 0.38, y + look[1] * r * 0.38
            if iris:
                E((px - r * 0.62, py - r * 0.78, px + r * 0.62, py + r * 0.78), iris, w=0)
            if slit:
                E((px - r * 0.17, py - r * 0.66, px + r * 0.17, py + r * 0.66), (20, 18, 22), w=0)
            else:
                E((px - r * 0.46, py - r * 0.52, px + r * 0.46, py + r * 0.52), (25, 20, 30), w=0)
            E((px - r * 0.42, py - r * 0.5, px - r * 0.06, py - r * 0.14), (255, 255, 255), w=0)
            if lid:
                d.chord([(x - r) * u, (y - r * 1.12) * u, (x + r) * u, (y + r * 1.12) * u],
                        180, 360, fill=lid)
                d.line([((x - r) * u, y * u), ((x + r) * u, y * u)], fill=OUTL, width=lw(2.6))
                d.ellipse([(x - r) * u, (y - r * 1.12) * u, (x + r) * u, (y + r * 1.12) * u],
                          outline=OUTL, width=lw(2.6))

    def mouth(x, y, wd, o):
        if o > 0.08:
            h = 4 + 16 * o
            E((x - wd / 2, y - h * 0.3, x + wd / 2, y + h), (125, 28, 48))
            E((x - wd * 0.3, y + h * 0.35, x + wd * 0.3, y + h * 0.95), (245, 115, 135), w=0)
        else:
            d.arc([(x - wd / 2) * u, (y - 8) * u, (x + wd / 2) * u, (y + 6) * u], 20, 160,
                  fill=OUTL, width=lw(3))

    if kind == "dog":
        fur, dark, cream = (214, 158, 98), (122, 78, 48), (252, 230, 198)
        sw = math.sin(T * 7) * (4 if talk > 0 else 1.5)
        E((18, 58 + sw, 64, 152 + sw), dark)
        E((136, 58 - sw, 182, 152 - sw), dark)
        E((40, 42, 160, 165), fur)
        E((108, 62, 146, 100), (236, 196, 146), w=0)  # eye patch
        E((66, 108, 134, 160), cream)
        E((52, 118, 68, 128), (255, 150, 150), w=0)
        E((132, 118, 148, 128), (255, 150, 150), w=0)
        eyes(80, 120, 90, 11.5)
        E((88, 103, 112, 120), (32, 22, 26))
        E((93, 106, 101, 111), (130, 120, 135), w=0)
        mouth(100, 138, 26, talk)
    elif kind == "cat":
        fur, dk, cream, pink = (246, 166, 76), (212, 118, 38), (255, 236, 210), (255, 160, 172)
        PG([(42, 86), (50, 18), (96, 52)], fur); PG([(56, 72), (57, 38), (82, 56)], pink, w=0)
        PG([(158, 86), (150, 18), (104, 52)], fur); PG([(144, 72), (143, 38), (118, 56)], pink, w=0)
        E((36, 44, 164, 160), fur)
        PG([(92, 46), (100, 68), (108, 46)], dk, w=0)
        PG([(70, 54), (80, 68), (85, 50)], dk, w=0)
        PG([(130, 54), (120, 68), (115, 50)], dk, w=0)
        E((74, 106, 126, 152), cream, w=0)
        eyes(77, 123, 92, 12.5, iris=(125, 205, 90), slit=True, lid=fur)
        PG([(93, 110), (107, 110), (100, 119)], pink, w=1.6)
        for s in (-1, 1):
            LN([(100 + s * 26, 124), (100 + s * 68, 115)], 1.6)
            LN([(100 + s * 26, 131), (100 + s * 68, 134)], 1.6)
        mouth(100, 132, 22, talk)
    elif kind == "cow":
        white, blk, pink, horn = (250, 250, 247), (42, 38, 44), (248, 180, 188), (238, 222, 182)
        E((50, 22, 68, 60), horn); E((132, 22, 150, 60), horn)
        E((12, 72, 60, 100), white); E((140, 72, 188, 100), white)
        E((22, 79, 52, 93), pink, w=0); E((148, 79, 178, 93), pink, w=0)
        E((42, 38, 158, 172), white)
        E((54, 50, 90, 86), blk, w=0); E((114, 58, 148, 94), blk, w=0)
        E((54, 114, 146, 176), pink)
        E((72, 128, 86, 142), (205, 115, 128), w=0); E((114, 128, 128, 142), (205, 115, 128), w=0)
        eyes(78, 122, 96, 11)
        mouth(100, 152, 28, talk)
    elif kind == "pigeon":
        body, neck, neck2, beak = (156, 166, 198), (92, 178, 146), (150, 104, 176), (238, 158, 64)
        E((34, 116, 166, 198), neck)
        E((50, 150, 150, 200), neck2, w=0)
        E((44, 34, 156, 150), body)
        eyes(78, 122, 84, 11, iris=(240, 140, 40))
        E((91, 96, 109, 107), (242, 242, 242), w=1.6)
        o = talk
        if o > 0.08:
            PG([(89, 117), (111, 117), (100, 128 + 12 * o)], (212, 128, 48))
        PG([(85, 104), (115, 104), (100, 124 - 4 * o)], beak)
    elif kind == "mosquito":
        wy = 14 * (0.5 + 0.5 * math.sin(T * 95))
        d.ellipse([70 * u, (28 + wy) * u, 122 * u, 88 * u], fill=(210, 232, 255, 150),
                  outline=(120, 140, 170, 220), width=lw(1.4))
        d.ellipse([96 * u, (22 + wy) * u, 152 * u, 86 * u], fill=(210, 232, 255, 130),
                  outline=(120, 140, 170, 220), width=lw(1.4))
        for x0, x1 in ((80, 60), (100, 96), (120, 140)):
            LN([(x0, 118), (x1, 150), (x1 - 8, 176)], 2.0, fill=(60, 50, 64))
        E((96, 92, 180, 126), (84, 72, 88))
        for xs in (118, 136, 154):
            LN([(xs, 94), (xs, 124)], 1.4, fill=(200, 200, 210))
        E((68, 80, 116, 126), (64, 54, 68))
        E((32, 70, 86, 120), (74, 62, 78))
        LN([(40, 104), (2, 124)], 2.3)
        for ex in (36, 58):
            E((ex, 74, ex + 22, 98), (222, 52, 64), w=1.4)
            E((ex + 8 + look[0] * 3, 82, ex + 15 + look[0] * 3, 90), (20, 16, 20), w=0)
            E((ex + 4, 77, ex + 9, 82), (255, 255, 255), w=0)
        if talk > 0.08:
            E((52, 104, 66, 106 + 8 * talk), (125, 28, 48), w=1.2)
        else:
            d.arc([50 * u, 100 * u, 66 * u, 110 * u], 20, 160, fill=OUTL, width=lw(2))
    return L.reduce(2)

# ---------------------------------------------------------------- sprites
def text_sprite(segments, size, path=F_TITLE, stroke=10, stroke_col=OUTL, shadow=True):
    f = font(size, path)
    total = sum(f.getlength(s) for s, _ in segments)
    asc, desc = f.getmetrics()
    pad = stroke + 22
    img = Image.new("RGBA", (int(total + 2 * pad), int(asc + desc + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if shadow:
        x = pad
        for s, _ in segments:
            d.text((x + 7, pad + 9), s, font=f, fill=(0, 0, 0, 110), stroke_width=stroke,
                   stroke_fill=(0, 0, 0, 110))
            x += f.getlength(s)
    x = pad
    for s, c in segments:
        d.text((x, pad), s, font=f, fill=c, stroke_width=stroke, stroke_fill=stroke_col)
        x += f.getlength(s)
    return img

def make_bubble(text):
    f = font(58)
    lines = wrap_words(text.split(), f, 820)
    lh, pad, tail, S = 76, 40, 56, 2
    tw = max(f.getlength(" ".join(l)) for l in lines)
    bw = int(tw + 2 * pad + 20); bh = int(len(lines) * lh + 2 * pad - 6)
    iw, ih = bw + 14, bh + tail + 14
    L = Image.new("RGBA", (iw * S, ih * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    cx = bw / 2
    d.rounded_rectangle([10 * S, 12 * S, (bw + 10) * S, (bh + 12) * S], radius=44 * S, fill=(0, 0, 0, 70))
    d.polygon([(x * S, y * S) for x, y in [(cx - 34, bh - 6), (cx + 30, bh - 6), (cx - 14, bh + tail)]],
              fill=WHITE, outline=OUTL, width=5 * S)
    d.rounded_rectangle([3 * S, 3 * S, (bw - 3) * S, (bh - 3) * S], radius=44 * S, fill=WHITE,
                        outline=OUTL, width=5 * S)
    d.polygon([(x * S, y * S) for x, y in [(cx - 27, bh - 12), (cx + 23, bh - 12), (cx - 13, bh + tail - 13)]],
              fill=WHITE)
    return dict(img=L.reduce(S), lines=lines, bw=bw, bh=bh, pad=pad, lh=lh, iw=iw, ih=ih)

def make_clock(label):
    f = font(46)
    tw = f.getlength(label); w = int(tw + 112); h = 84; S = 2
    L = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=42 * S, fill=(18, 14, 34, 210))
    cx, cy, r = 46, 42, 21
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=YEL, width=5 * S)
    d.line([(cx * S, cy * S), (cx * S, (cy - 12) * S)], fill=YEL, width=5 * S)
    d.line([(cx * S, cy * S), ((cx + 10) * S, cy * S)], fill=YEL, width=5 * S)
    L = L.reduce(S)
    ImageDraw.Draw(L).text((84, h / 2 + 2), label, font=f, fill=WHITE, anchor="lm")
    return L

def glow_sun(r=170):
    S = 2; size = r * 4
    L = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = size * S / 2
    for i in range(14, 0, -1):
        rr = r * S * (1 + i * 0.07)
        d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=(255, 236, 160, 14))
    d.ellipse([c - r * S, c - r * S, c + r * S, c + r * S], fill=(255, 226, 120))
    d.ellipse([c - r * S * 0.8, c - r * S * 0.8, c + r * S * 0.8, c + r * S * 0.8], fill=(255, 240, 170))
    return L.reduce(S)

def phone_sprite():
    S = 2; w, h = 150, 78
    L = Image.new("RGBA", ((w + 8) * S, (h + 8) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([4 * S, 4 * S, (w + 4) * S, (h + 4) * S], radius=16 * S, fill=(30, 30, 40),
                        outline=OUTL, width=4 * S)
    d.rounded_rectangle([14 * S, 12 * S, (w - 6) * S, (h - 4) * S], radius=8 * S, fill=(90, 170, 250))
    d.ellipse([(w - 2) * S, 34 * S, (w + 2) * S, 46 * S], fill=(70, 70, 80))
    return L.reduce(S)

# ---------------------------------------------------------------- backgrounds
def grad(stops, w, h):
    ys = np.linspace(0, 1, h)
    pos = [p for p, _ in stops]
    cols = np.array([c for _, c in stops], float)
    a = np.stack([np.interp(ys, pos, cols[:, i]) for i in range(3)], axis=1)  # h x 3
    a = np.repeat(a[:, None, :], w, axis=1)
    alpha = np.full((h, w, 1), 255.0)
    return Image.fromarray(np.concatenate([a, alpha], 2).astype(np.uint8), "RGBA")

def build_bg(kind):
    k = 2
    rng = np.random.default_rng(hash(kind) % 1000)
    G = {
        "intro": [(0, (22, 10, 56)), (1, (96, 28, 124))],
        "outro": [(0, (22, 10, 56)), (1, (96, 28, 124))],
        "dawn": [(0, (96, 84, 190)), (0.45, (250, 140, 120)), (0.75, (255, 200, 130)), (1, (255, 220, 150))],
        "dog": [(0, (255, 228, 184)), (1, (252, 198, 148))],
        "cat": [(0, (156, 218, 212)), (1, (104, 180, 186))],
        "cow": [(0, (112, 184, 250)), (0.7, (204, 236, 255)), (1, (204, 236, 255))],
        "pigeon": [(0, (255, 160, 118)), (0.7, (255, 214, 160)), (1, (255, 226, 170))],
        "mosquito": [(0, (12, 16, 50)), (1, (50, 34, 96))],
        "twist": [(0, (6, 6, 22)), (1, (28, 22, 60))],
    }[kind]
    img = grad(G, W * k, H * k)
    d = ImageDraw.Draw(img)
    def E(b, fill): d.ellipse([v * k for v in b], fill=fill)
    def R(b, fill, r=0):
        if r: d.rounded_rectangle([v * k for v in b], radius=r * k, fill=fill)
        else: d.rectangle([v * k for v in b], fill=fill)
    def PG(pts, fill): d.polygon([(x * k, y * k) for x, y in pts], fill=fill)
    def LN(pts, fill, w): d.line([(x * k, y * k) for x, y in pts], fill=fill, width=w * k)

    if kind in ("intro", "outro"):
        for i, rr in enumerate([900, 720, 540, 360]):
            c = (40 + i * 10, 18 + i * 5, 84 + i * 12)
            E((540 - rr, 960 - rr, 540 + rr, 960 + rr), c)
        for _ in range(60):
            x, y = rng.uniform(0, W), rng.uniform(0, H); r = rng.uniform(2, 5)
            E((x - r, y - r, x + r, y + r), (200, 170, 255))
    elif kind == "dawn":
        for _ in range(25):
            x, y = rng.uniform(0, W), rng.uniform(0, 600); r = rng.uniform(2, 4)
            E((x - r, y - r, x + r, y + r), (255, 240, 255))
    elif kind == "dog":
        R((800, 860, 1040, 1180), (120, 78, 52), 16); R((818, 878, 1022, 1162), (150, 212, 255), 8)
        E((850, 960, 950, 1020), WHITE); E((900, 940, 990, 1010), WHITE)
        LN([(920, 878), (920, 1162)], (120, 78, 52), 10); LN([(818, 1020), (1022, 1020)], (120, 78, 52), 10)
        R((40, 900, 260, 1080), (120, 78, 52), 10); R((56, 916, 244, 1064), (252, 244, 226), 6)
        E((90, 960, 126, 996), (230, 220, 200)); E((90, 984, 126, 1020), (230, 220, 200))
        E((174, 960, 210, 996), (230, 220, 200)); E((174, 984, 210, 1020), (230, 220, 200))
        R((108, 974, 192, 1006), (230, 220, 200))
        R((0, 1330, 1080, 1920), (178, 118, 74))
        for y in range(1400, 1920, 90):
            LN([(0, y), (1080, y)], (150, 96, 58), 4)
        E((120, 1290, 960, 1450), (214, 84, 92)); E((190, 1312, 890, 1428), (238, 128, 122))
    elif kind == "cat":
        for y in range(820, 1290, 70):
            LN([(0, y), (1080, y)], (140, 204, 202), 3)
        for x in range(0, 1080, 70):
            LN([(x, 820), (x, 1290)], (140, 204, 202), 3)
        R((0, 1286, 1080, 1330), (170, 110, 68)); R((0, 1286, 1080, 1296), (200, 140, 92))
        R((0, 1330, 1080, 1920), (124, 78, 50))
        R((120, 1196, 210, 1288), WHITE, 10); d.arc([200 * k, 1216 * k, 246 * k, 1264 * k], 270, 90, fill=WHITE, width=10 * k)
        E((132, 1204, 198, 1222), (120, 72, 40))
    elif kind == "cow":
        for cx, cy in ((220, 380), (820, 300), (600, 520)):
            for dx, r in ((-60, 50), (0, 70), (60, 50)):
                E((cx + dx - r, cy - r, cx + dx + r, cy + r), (255, 255, 255))
        E((-200, 1120, 700, 1500), (130, 200, 110)); E((400, 1100, 1300, 1500), (120, 190, 100))
        R((60, 1060, 280, 1220), (196, 58, 52)); PG([(40, 1070), (170, 970), (300, 1070)], (150, 40, 40))
        R((130, 1130, 210, 1220), (250, 240, 230))
        LN([(130, 1130), (210, 1220)], (196, 58, 52), 6); LN([(210, 1130), (130, 1220)], (196, 58, 52), 6)
        R((0, 1280, 1080, 1920), (112, 192, 92))
        for x in range(20, 1080, 130):
            R((x, 1210, x + 22, 1320), (236, 222, 196), 4)
        R((0, 1232, 1080, 1246), (236, 222, 196)); R((0, 1276, 1080, 1290), (236, 222, 196))
        for _ in range(40):
            x, y = rng.uniform(0, W), rng.uniform(1340, H)
            PG([(x, y), (x + 8, y - 26), (x + 16, y)], (90, 170, 76))
    elif kind == "pigeon":
        x = 0
        while x < 1080:
            bw = rng.integers(90, 170); top = rng.integers(860, 1150)
            R((x, top, x + bw, 1310), (122, 82, 134))
            for wy in range(int(top) + 30, 1290, 60):
                for wx in range(int(x) + 18, int(x + bw) - 24, 40):
                    if rng.random() < 0.55:
                        R((wx, wy, wx + 18, wy + 26), (255, 214, 120))
            x += bw + rng.integers(4, 20)
        R((0, 1300, 1080, 1344), (88, 66, 92)); R((0, 1344, 1080, 1920), (66, 52, 74))
        E((770, 1274, 1010, 1316), (245, 245, 250))
        PG([(808, 1290), (972, 1290), (890, 1158)], (232, 172, 68))
        LN([(890, 1158), (868, 1290)], (196, 132, 44), 4); LN([(850, 1230), (930, 1230)], (196, 132, 44), 3)
    elif kind == "mosquito":
        for _ in range(70):
            x, y = rng.uniform(0, W), rng.uniform(0, 1100); r = rng.uniform(1.5, 4)
            E((x - r, y - r, x + r, y + r), (230, 230, 255))
        E((820, 330, 980, 490), (250, 242, 205)); E((860, 370, 892, 402), (232, 222, 182)); E((910, 420, 936, 446), (232, 222, 182))
        R((140, 1140, 940, 1262), (92, 62, 112), 30)
        E((300, 1170, 780, 1300), (232, 232, 246))
        E((470, 1136, 612, 1278), (242, 194, 154))
        d.chord([470 * k, 1136 * k, 612 * k, 1278 * k], 180, 360, fill=(52, 36, 34))
        d.arc([500 * k, 1206 * k, 530 * k, 1224 * k], 200, 340, fill=OUTL, width=4 * k)
        d.arc([552 * k, 1206 * k, 582 * k, 1224 * k], 200, 340, fill=OUTL, width=4 * k)
        R((60, 1250, 1020, 1920), (74, 92, 176), 60)
        for y in range(1330, 1920, 110):
            LN([(60, y), (1020, y)], (90, 110, 196), 6)
    elif kind == "twist":
        for _ in range(90):
            x, y = rng.uniform(0, W), rng.uniform(0, 1250); r = rng.uniform(1.5, 4)
            E((x - r, y - r, x + r, y + r), (230, 230, 255))
        E((80, 300, 220, 440), (250, 242, 205)); E((114, 286, 252, 424), (6, 6, 24))
        R((0, 1330, 1080, 1920), (30, 24, 48))
        cone = Image.new("RGBA", img.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(cone)
        cd.polygon([(470 * k, 0), (610 * k, 0), (900 * k, 1380 * k), (180 * k, 1380 * k)], fill=(255, 240, 200, 34))
        cd.ellipse([180 * k, 1310 * k, 900 * k, 1450 * k], fill=(255, 240, 200, 52))
        img = Image.alpha_composite(img, cone)
    return img.reduce(k)

def build_hills():
    k = 2
    L = Image.new("RGBA", (W * k, 700 * k), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse([-400 * k, 70 * k, 760 * k, 1100 * k], fill=(78, 150, 96))
    d.ellipse([360 * k, 110 * k, 1500 * k, 1100 * k], fill=(56, 122, 80))
    d.rectangle([0, 420 * k, W * k, 700 * k], fill=(56, 122, 80))
    return L.reduce(k)  # placed at y = 1220

# ---------------------------------------------------------------- script
SCENES = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="dawn", s=4.0, e=8.5, clock="6:00 AM",
         narr="Every animal on Earth wakes up... and starts TALKING.", n_at=4.3),
    dict(id="dog", s=8.5, e=16.0, clock="8:00 AM", narr="Your dog goes FIRST.", n_at=8.7,
         animal="dog", say="You left me ALONE for 8 hours. I thought you were DEAD!", say_at=9.7,
         look=(0, 0.15), pitch=320),
    dict(id="cat", s=16.0, e=23.5, clock="10:30 AM", narr="Your cat finally CONFESSES.", n_at=16.2,
         animal="cat", say="I pushed your phone off the table. On purpose. Zero regrets.", say_at=17.2,
         look=(0.7, 0), pitch=540),
    dict(id="cow", s=23.5, e=31.0, clock="1:00 PM", narr="Dairy farms get VERY awkward.", n_at=23.7,
         animal="cow", say="So... about the milk. We need to TALK.", say_at=24.9,
         look=(0, 0.2), pitch=165),
    dict(id="pigeon", s=31.0, e=38.0, clock="5:00 PM", narr="Pigeons demand their SHARE.", n_at=31.2,
         animal="pigeon", say="10 years we watched you eat samosas. PAY UP.", say_at=32.2,
         look=(0.8, 0.4), pitch=660),
    dict(id="mosquito", s=38.0, e=44.5, clock="10:00 PM", narr="Some animals you'd rather NOT hear...",
         n_at=38.2, animal="mosquito", say="Nothing personal. Just hungry.", say_at=39.5,
         look=(0, 0), pitch=900),
    dict(id="twist", s=44.5, e=51.0, clock="11:59 PM", narr="The world goes silent... except ONE.",
         n_at=44.8, animal="dog", say="Same time next year?", say_at=47.6, look=(0, 0), pitch=320,
         enter=46.5),
    dict(id="outro", s=51.0, e=56.0),
]
for sc in SCENES:
    if "say" in sc:
        sc["say_end"] = sc["say_at"] + len(sc["say"]) * CPS
CAT = next(s for s in SCENES if s["id"] == "cat")
PHONE_PUSH = CAT["say_at"] + CAT["say"].index("On purpose") * CPS
PHONE_CRASH = PHONE_PUSH + 0.35 + 0.62
WINK_AT = 49.4

# ---------------------------------------------------------------- assets
print("building assets...", flush=True)
BG = {sc["id"]: build_bg(sc["id"]) for sc in SCENES}
HILLS = build_hills()
SUN = glow_sun()
PHONE = phone_sprite()
BUB = {sc["id"]: make_bubble(sc["say"]) for sc in SCENES if "say" in sc}
CLK = {sc["id"]: make_clock(sc["clock"]) for sc in SCENES if "clock" in sc}
T_WHATIF = text_sprite([("WHAT IF", YEL)], 220)
T_ANIMALS = text_sprite([("ANIMALS", WHITE)], 140)
T_COULD = text_sprite([("COULD TALK", WHITE)], 140)
T_ONEDAY = text_sprite([("...for just ", WHITE), ("ONE DAY?", YEL)], 84)
T_O1 = text_sprite([("Which animal would", WHITE)], 84)
T_O2 = text_sprite([("roast ", YEL), ("YOU", WHITE), (" first?", YEL)], 116)
T_FOLLOW = text_sprite([("Follow for more ", WHITE), ("WHAT IFs", YEL)], 56, stroke=7)
def pill(text):
    f = font(60, F_TITLE); tw = f.getlength(text); w, h = int(tw + 90), 116; S = 2
    L = Image.new("RGBA", (w * S + 20, h * S + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([10, 14, w * S + 10, h * S + 14], radius=h * S // 2, fill=(0, 0, 0, 90))
    d.rounded_rectangle([0, 0, w * S, h * S], radius=h * S // 2, fill=YEL, outline=OUTL, width=8)
    L = L.reduce(S)
    ImageDraw.Draw(L).text((w / 2, h / 2 - 2), text, font=f, fill=OUTL, anchor="mm")
    return L
T_COMMENT = pill("COMMENT BELOW")

def blink_at(T, seed): return ((T * 0.37 + seed) % 1.0) < 0.045

def talk_amt(sc, T):
    if "say" in sc and sc["say_at"] <= T < sc["say_end"]:
        return clamp(0.5 + 0.55 * math.sin(T * 27))
    return 0.0

# ---------------------------------------------------------------- frame
def scene_at(T):
    for sc in SCENES:
        if sc["s"] <= T < sc["e"]:
            return sc
    return SCENES[-1]

def draw_narr(frame, sc, T):
    if "narr" not in sc or T < sc["n_at"]:
        return
    d = ImageDraw.Draw(frame)
    f = font(66)
    words = sc["narr"].split()
    lines = wrap_words(words, f, 880)
    n = int((T - sc["n_at"]) / 0.2) + 1
    lh = 86; y0 = 1470 - len(lines) * lh / 2
    idx = 0
    for li, line in enumerate(lines):
        GAP = 20
        x = 540 - (f.getlength(" ".join(line)) + GAP * (len(line) - 1)) / 2; y = y0 + li * lh
        for w in line:
            if idx < n:
                age = T - (sc["n_at"] + idx * 0.2)
                dy = -14 * (1 - ease_out(age / 0.15))
                d.text((x, y + dy), w, font=f, fill=YEL if is_emph(w) else WHITE,
                       stroke_width=8, stroke_fill=(0, 0, 0))
            x += f.getlength(w + " ") + GAP; idx += 1

def draw_bubble(frame, sc, T, anchor_y=800):
    if "say" not in sc:
        return
    t0 = sc["say_at"] - 0.25
    if T < t0:
        return
    B = BUB[sc["id"]]
    b = B["img"].copy(); bd = ImageDraw.Draw(b)
    f = font(58)
    nvis = int((T - sc["say_at"]) / CPS) + 1 if T >= sc["say_at"] else 0
    count = 0
    for li, line in enumerate(B["lines"]):
        x = (B["bw"] - f.getlength(" ".join(line))) / 2
        y = B["pad"] - 6 + li * B["lh"]
        for w in line:
            vis = w[:max(0, nvis - count)]
            if vis:
                bd.text((x, y), vis, font=f, fill=RED if is_emph(w) else (36, 26, 46))
            x += f.getlength(w + " ")
            count += len(w) + 1
    s = 0.35 + 0.65 * ease_back((T - t0) / 0.3)
    bb = b.resize((max(1, int(b.width * s)), max(1, int(b.height * s))), Image.BILINEAR) if abs(s - 1) > 0.01 else b
    comp(frame, bb, 540 - B["bw"] * s / 2, anchor_y + 60 - bb.height)

def draw_clock(frame, sc, T):
    if sc["id"] not in CLK:
        return
    lt = T - sc["s"] - 0.25
    if lt < 0:
        return
    c = CLK[sc["id"]]
    y = 228 - 60 * (1 - ease_back(lt / 0.35))
    comp(frame, c, 540 - c.width / 2, y)

def render(T):
    sc = scene_at(T); lt = T - sc["s"]; sid = sc["id"]
    frame = BG[sid].copy()
    d = ImageDraw.Draw(frame)

    if sid == "intro":
        if T >= 0.2: paste_c(frame, T_WHATIF, 540, 600, 0.2 + 0.8 * ease_back((T - 0.2) / 0.35))
        if T >= 0.75: paste_c(frame, T_ANIMALS, 540 + 600 * (1 - ease_out((T - 0.75) / 0.3)), 820)
        if T >= 1.05: paste_c(frame, T_COULD, 540 - 600 * (1 - ease_out((T - 1.05) / 0.3)), 965)
        if T >= 1.5: paste_c(frame, T_ONEDAY, 540, 1110, 0.3 + 0.7 * ease_back((T - 1.5) / 0.3))
        if T >= 1.9:
            a = ease_out((T - 1.9) / 0.3)
            cols = [YEL, WHITE, (255, 140, 180)]
            for i in range(13):
                x = 540 + (i - 6) * 62
                hgt = (30 + 110 * abs(math.sin(T * (5 + i % 4) + i * 1.3))) * a
                d.rounded_rectangle([x - 18, 1360 - hgt, x + 18, 1360 + hgt], radius=18, fill=cols[i % 3])
    elif sid == "outro":
        if lt >= 0.15: paste_c(frame, T_O1, 540, 470, 0.3 + 0.7 * ease_back((lt - 0.15) / 0.3))
        if lt >= 0.45:
            wob = 1 + 0.03 * math.sin(T * 6)
            paste_c(frame, T_O2, 540, 610, (0.3 + 0.7 * ease_back((lt - 0.45) / 0.3)) * wob)
        kinds = ["dog", "cat", "cow", "pigeon", "mosquito"]
        for i, kd in enumerate(kinds):
            st = 0.9 + i * 0.18
            if lt < st: continue
            p = ease_back((lt - st) / 0.35)
            x = 540 + (i - 2) * 205; y = 940 + 300 * (1 - p) + 10 * math.sin(T * 4 + i)
            talk = clamp(0.5 + 0.6 * math.sin(T * 22 + i * 2)) if 1.8 <= lt < 3.6 else 0
            spr = draw_animal(kd, 200, T, talk, blink_at(T, i * 0.2), (0, 0.2))
            comp(frame, spr, x - 100, y - 100)
        if lt >= 2.2:
            paste_c(frame, T_COMMENT, 540, 1235, (0.3 + 0.7 * ease_back((lt - 2.2) / 0.3)) * (1 + 0.04 * math.sin(T * 7)))
            ay = 1360 + 18 * abs(math.sin(T * 5))
            d.polygon([(500, ay), (580, ay), (540, ay + 60)], fill=WHITE, outline=OUTL, width=5)
        if lt >= 2.6:
            paste_c(frame, T_FOLLOW, 540, 1530, 0.3 + 0.7 * ease_back((lt - 2.6) / 0.3))
    elif sid == "dawn":
        sy = 1500 - 520 * ease_out(lt / 3.2)
        paste_c(frame, SUN, 760, sy)
        comp(frame, HILLS, 0, 1220)
        kinds = ["dog", "cat", "cow", "pigeon"]
        for i, kd in enumerate(kinds):
            st = 1.6 + i * 0.25
            if lt < st: continue
            p = ease_back((lt - st) / 0.4)
            x = 540 + (i - 1.5) * 255; y = 1215 + 330 * (1 - p)
            talk = clamp(0.5 + 0.6 * math.sin(T * 24 + i * 1.7)) if 2.9 <= lt < 4.3 else 0
            look = (math.sin(T + i), 0.2)
            spr = draw_animal(kd, 250, T, talk, blink_at(T, i * 0.3), look)
            comp(frame, spr, x - 125, y - 125)
    else:
        # scene props
        if sid == "cat":
            if T < PHONE_PUSH:
                px, py, rot = 840, 1250, 0
            else:
                u_ = T - PHONE_PUSH
                if u_ < 0.35:
                    px, py, rot = 840 + 180 * ease_out(u_ / 0.35), 1250, 0
                else:
                    v = u_ - 0.35
                    px, py, rot = 1020 + 240 * v, 1250 + 1900 * v * v, -400 * v
            spr = PHONE.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else PHONE
            if py < H + 100:
                comp(frame, spr, px - spr.width / 2, py - spr.height / 2)
        if sid == "mosquito":
            fz = font(54)
            for j in range(3):
                ph = ((T * 0.5) + j / 3) % 1.0
                d.text((610 + 70 * ph + j * 4, 1130 - 200 * ph), "z" if j % 2 else "Z", font=fz,
                       fill=(190, 200, 255), stroke_width=3, stroke_fill=(40, 40, 90))
        # character
        enter = sc.get("enter", sc["s"] + 0.15)
        if T >= enter:
            le = T - enter
            talk = talk_amt(sc, T)
            if sid == "mosquito":
                B = 430
                tt = T - sc["s"]
                x = 540 + 170 * math.sin(1.25 * tt) + 40 * math.sin(5.3 * tt)
                y = 930 + 60 * math.sin(2.1 * tt) + 22 * math.cos(6.4 * tt)
                if le < 0.8:
                    x = -300 + (x + 300) * ease_out(le / 0.8)
                spr = draw_animal("mosquito", B, T, talk, False, (0, 0))
                comp(frame, spr, x - B / 2, y - B / 2)
            else:
                B = 640
                p = ease_back(le / 0.55)
                bob = 8 * math.sin(T * 3.2) + (6 * math.sin(T * 20) if talk > 0 else 0)
                y = 1060 + 620 * (1 - p) + bob
                wink = sid == "twist" and T >= WINK_AT
                spr = draw_animal(sc["animal"], B, T, talk, blink_at(T, 0.5) and not wink,
                                  sc.get("look", (0, 0)), wink)
                comp(frame, spr, 540 - B / 2, y - B / 2)
        draw_bubble(frame, sc, T)

    draw_clock(frame, sc, T)
    draw_narr(frame, sc, T)

    # transitions: punch-in zoom + flash
    if sid != "intro" and lt < 0.2:
        s = 1.0 + 0.07 * (1 - ease_out(lt / 0.2))
        big = frame.resize((int(W * s), int(H * s)), Image.BILINEAR)
        ox, oy = (big.width - W) // 2, (big.height - H) // 2
        frame = big.crop((ox, oy, ox + W, oy + H))
        if lt < 0.12:
            frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.55 * (1 - lt / 0.12))
    # gentle fade-in at very start
    if T < 0.2:
        frame = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), frame, T / 0.2)
    return frame.convert("RGB")

# ---------------------------------------------------------------- audio
def build_audio(path):
    N = int(SR * (TOTAL + 1))
    music = np.zeros(N); fx = np.zeros(N)
    rng = np.random.default_rng(7)
    tarr = lambda dd: np.arange(int(dd * SR)) / SR

    def add(buf, sig, t, g=1.0):
        i = int(round(t * SR))
        if i >= N: return
        if i < 0: sig = sig[-i:]; i = 0
        j = min(N, i + len(sig)); buf[i:j] += sig[:j - i] * g

    def lp(x, k):
        if k <= 1: return x.copy()
        pad = np.concatenate([np.full(k // 2, x[0]), x, np.full(k - k // 2, x[-1])])
        c = np.concatenate([[0.0], np.cumsum(pad)])
        return (c[k:k + len(x)] - c[:len(x)]) / k

    osc = lambda f: 2 * np.pi * np.cumsum(f) / SR
    mf = lambda m: 440 * 2 ** ((m - 69) / 12)
    def fadeout(s, ms=10):
        L = min(len(s), int(ms / 1000 * SR)); s[-L:] *= np.linspace(1, 0, L); return s

    # instruments
    def kick():
        t = tarr(0.35); f = 45 + 110 * np.exp(-t * 22)
        return np.sin(osc(f)) * np.exp(-t * 9)
    def clap():
        t = tarr(0.18); n = rng.standard_normal(len(t)); n = n - lp(n, 8)
        return n * np.exp(-t * 28) * 0.5
    def hat():
        t = tarr(0.05); n = rng.standard_normal(len(t)); n = n - lp(n, 3)
        return n * np.exp(-t * 90) * 0.25
    def pluck(f, dd=0.32):
        t = tarr(dd); ph = 2 * np.pi * f * t
        s = np.sin(ph) + 0.5 * np.sin(2 * ph) * np.exp(-t * 6) + 0.25 * np.sin(3 * ph) * np.exp(-t * 10)
        return fadeout(s * np.minimum(1, t / 0.003) * np.exp(-t * 9))
    def bassn(f, dd=0.45):
        t = tarr(dd); ph = 2 * np.pi * f * t
        tri = 2 / np.pi * np.arcsin(np.sin(ph))
        return fadeout((0.7 * tri + 0.5 * np.sin(ph)) * np.minimum(1, t / 0.004) * np.exp(-t * 4.5))
    def bell(f, dd=0.4):
        t = tarr(dd); s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 8)
        return fadeout(s * np.minimum(1, t / 0.002) * np.exp(-t * 7))

    BPM = 112; beat = 60 / BPM
    roots = [48, 43, 45, 41]
    chords = [(60, 64, 67), (59, 62, 67), (57, 60, 64), (57, 60, 65)]
    mel = [  # per bar: (beat offset, midi)
        [(0, 76), (1, 79), (1.5, 76), (2.5, 72), (3, 74)],
        [(0, 74), (1, 71), (1.5, 74), (2.5, 79), (3, 77)],
        [(0, 76), (1, 72), (1.5, 76), (2.5, 81), (3, 79)],
        [(0, 77), (1, 76), (1.5, 74), (2.5, 72), (3, 71)],
    ]
    def groove(t0, t1, drums=True, melody=False):
        b = 0
        while True:
            t = t0 + b * beat
            if t >= t1 - 0.05: break
            bar = (b // 4) % 4; pos = b % 4
            if drums:
                if pos in (0, 2): add(music, kick(), t, 0.85)
                if pos in (1, 3): add(music, clap(), t, 0.45)
                add(music, hat(), t + beat / 2, 0.6); add(music, hat(), t, 0.3)
            add(music, bassn(mf(roots[bar])), t, 0.5)
            for m in chords[bar]:
                add(music, pluck(mf(m)), t + beat / 2, 0.13)
            if melody and pos == 0:
                for off, m in mel[bar]:
                    if t + off * beat < t1 - 0.05:
                        add(music, bell(mf(m)), t + off * beat, 0.16)
            b += 1

    groove(0.2, 4.0, drums=False)
    groove(4.0, 44.45, drums=True, melody=False)
    # gentle pad during the twist
    t = tarr(6.4); env = np.minimum(1, t / 1.5) * np.minimum(1, (6.4 - t) / 1.0)
    pad = sum(np.sin(2 * np.pi * mf(m - 12) * t) for m in (57, 60, 64)) * env * 0.05
    add(music, pad, 44.6)
    groove(51.0, 56.0, drums=True, melody=True)

    # sfx
    def whoosh(dd=0.45):
        t = tarr(dd); n = rng.standard_normal(len(t))
        env = np.sin(np.pi * t / dd) ** 2
        return (lp(n, 14) * 1.3 + 0.25 * (n - lp(n, 4)) * (t / dd)) * env * 0.45
    def boom():
        t = tarr(1.4); f = 38 + 60 * np.exp(-t * 6)
        return (np.sin(osc(f)) * np.exp(-t * 3) + lp(rng.standard_normal(len(t)), 20) * np.exp(-t * 12) * 0.6) * 0.9
    def pop():
        t = tarr(0.09); f = 500 + 900 * t / 0.09
        return np.sin(osc(f)) * np.sin(np.pi * t / 0.09) * 0.45
    def tick():
        t = tarr(0.05); return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 150) * 0.45
    def blip(f, g=1.0):
        t = tarr(0.055); ff = f * (1 + 0.25 * np.exp(-t * 80)); ph = osc(ff)
        s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph)
        return fadeout(s * np.minimum(1, t / 0.004) * np.exp(-t * 30) * 0.26 * g)
    def bark():
        t = tarr(0.2); f = 260 + 380 * np.exp(-t * 18); ph = osc(f)
        s = np.tanh(2.5 * (np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sin(3 * ph)))
        n = lp(rng.standard_normal(len(t)), 3) * 0.35
        return fadeout(lp((s + n) * np.minimum(1, t / 0.006) * np.exp(-t * 16), 3) * 0.55)
    def meow():
        dd = 0.75; t = tarr(dd); x = t / dd
        f = 430 + 360 * np.sin(np.pi * x) * (1 - 0.45 * x); ph = osc(f)
        br = np.sin(np.pi * x)
        s = np.sin(ph) + (0.2 + 0.7 * br) * np.sin(2 * ph) + (0.1 + 0.5 * br) * np.sin(3 * ph) + 0.3 * br * np.sin(4 * ph)
        return s * np.minimum(1, t / 0.06) * np.minimum(1, (dd - t) / 0.15) * 0.3
    def moo():
        dd = 1.3; t = tarr(dd); x = t / dd
        f = 150 - 25 * x + 3 * np.sin(2 * np.pi * 5 * t); ph = osc(f)
        op = np.sin(np.pi * np.clip(x * 1.2, 0, 1))
        s = sum((1 / kk) * (op if kk > 2 else 1) * np.sin(kk * ph) for kk in range(1, 10))
        return lp(s, 4) * np.minimum(1, t / 0.12) * np.minimum(1, (dd - t) / 0.3) * 0.38
    def coo():
        out = []
        for f0, f1, dd in ((300, 330, 0.18), (330, 250, 0.45)):
            t = tarr(dd); f = f0 + (f1 - f0) * t / dd; ph = osc(f)
            s = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * (0.75 + 0.25 * np.sin(2 * np.pi * 22 * t))
            out += [s * np.minimum(1, t / 0.03) * np.minimum(1, (dd - t) / 0.08), np.zeros(int(0.04 * SR))]
        return np.concatenate(out) * 0.42
    def crash():
        t = tarr(0.6); n = rng.standard_normal(len(t)); n = n - lp(n, 2)
        s = n * np.exp(-t * 10) * 0.5 + np.sin(2 * np.pi * 170 * t) * np.exp(-t * 30) * 0.6
        for _ in range(12):
            t0 = rng.uniform(0, 0.35); f = rng.uniform(2500, 6000); tt = t - t0; m = tt > 0
            s[m] += np.sin(2 * np.pi * f * tt[m]) * np.exp(-tt[m] * 40) * 0.15
        return s * 0.7
    def scratch():
        dd = 0.45; t = tarr(dd)
        f = np.where(t < 0.18, 300 + 900 * t / 0.18, 1200 - 1000 * (t - 0.18) / 0.27); ph = osc(f)
        s = np.sign(np.sin(ph)) * 0.3 + lp(rng.standard_normal(len(t)), 2) * 0.4
        return lp(s * np.minimum(1, t / 0.01) * np.minimum(1, (dd - t) / 0.05), 3) * 0.5
    def ding(f=1320):
        t = tarr(1.6)
        s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 3) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
             + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9))
        return s * np.minimum(1, t / 0.002) * 0.4
    def crickets(dd):
        t = tarr(dd); s = np.zeros(len(t)); L = int(0.03 * SR)
        for kk in range(int(dd / 0.85) + 1):
            for j in range(3):
                i = int((kk * 0.85 + j * 0.045 + (0.15 if kk % 2 else 0)) * SR)
                if i + L < len(t): s[i:i + L] += np.sin(np.linspace(0, np.pi, L))
        return np.sin(2 * np.pi * 4300 * t) * s * 0.05
    def babble(text, t0, base, g=1.0, cps=CPS):
        for i, ch in enumerate(text):
            if ch.isalnum():
                f = base * 2 ** ((((ord(ch.lower()) * 5) % 9) - 4) / 14)
                add(fx, blip(f, 1.3 if ch.isupper() else 1.0), t0 + i * cps, g)

    # intro
    add(fx, boom(), 0.2); add(fx, pop(), 0.75); add(fx, pop(), 1.05); add(fx, pop(), 1.5, 1.2)
    letters = "abcdefghijklmnopqrstuvwxyz"
    for j, base in enumerate((320, 540, 165, 660)):
        babble("".join(letters[(i * 7 + j * 3) % 26] for i in range(26)), 2.0 + j * 0.03, base, 0.45, 0.065)
    # scene transitions + clocks
    for sc in SCENES[1:]:
        add(fx, whoosh(), sc["s"] - 0.2)
        if "clock" in sc: add(fx, tick(), sc["s"] + 0.25)
    # dawn
    for i in range(4): add(fx, pop(), 4.0 + 1.6 + i * 0.25)
    for j, base in enumerate((320, 540, 165, 660)):
        babble("".join(letters[(i * 5 + j * 7) % 26] for i in range(20)), 6.9 + j * 0.02, base, 0.45, 0.07)
    # speeches
    for sc in SCENES:
        if "say" in sc:
            babble(sc["say"], sc["say_at"], sc["pitch"], 1.0)
    dog, cat, cow, pig, mos, tw = (next(s for s in SCENES if s["id"] == k) for k in
                                   ("dog", "cat", "cow", "pigeon", "mosquito", "twist"))
    add(fx, bark(), dog["s"] + 0.3); add(fx, bark(), dog["s"] + 0.55, 0.9)
    add(fx, meow(), cat["s"] + 0.35)
    add(fx, whoosh(0.3), PHONE_PUSH, 0.6); add(fx, crash(), PHONE_CRASH)
    add(fx, moo(), cow["s"] + 0.25)
    add(fx, coo(), pig["s"] + 0.35)
    dd = mos["e"] - mos["s"]
    t = tarr(dd); f = 560 + 30 * np.sin(2 * np.pi * 5.5 * t) + 18 * np.sin(2 * np.pi * 1.3 * t)
    ph = osc(f); s = sum(np.sin(kk * ph) / kk for kk in range(1, 9))
    amp = (0.6 + 0.4 * np.sin(1.25 * t)) * np.minimum(1, t / 0.5) * np.minimum(1, (dd - t) / 0.3)
    add(fx, s * amp * 0.11, mos["s"])
    add(fx, scratch(), 44.35, 1.0)
    add(fx, crickets(6.4), 44.6)
    add(fx, pop(), tw["enter"] + 0.05)
    add(fx, ding(), WINK_AT)
    # outro
    add(fx, boom(), 51.05, 0.6)
    for i in range(5): add(fx, pop(), 51.0 + 0.9 + i * 0.18)
    add(fx, pop(), 53.2, 1.2)
    add(fx, ding(1760), 55.0, 0.6)

    # mix with ducking
    gain = np.full(N, 0.6)
    for sc in SCENES:
        if "say" in sc:
            gain[int((sc["say_at"] - 0.2) * SR):int((sc["say_end"] + 0.2) * SR)] = 0.33
    gain = lp(gain, int(0.15 * SR))
    tot = np.arange(N) / SR
    gain *= np.clip((TOTAL - tot) / 0.8, 0, 1)
    mix = music * gain + fx * np.clip((TOTAL + 0.05 - tot) / 0.3, 0, 1)
    mix = np.tanh(mix * 1.2)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.9
    mix = mix[:int(TOTAL * SR)]
    pcm = (mix * 32767).astype(np.int16)
    stereo = np.stack([pcm, pcm], 1).reshape(-1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "preview":
        times = [float(x) for x in sys.argv[2].split(",")]
        frames = [render(t) for t in times]
        tw_, th_ = 270, 480
        cols = 4; rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw_, rows * th_), (0, 0, 0))
        for i, fr in enumerate(frames):
            sheet.paste(fr.resize((tw_, th_)), ((i % cols) * tw_, (i // cols) * th_))
        sheet.save(os.path.join(HERE, "preview.png"))
        for t, fr in zip(times, frames):
            fr.save(os.path.join(HERE, f"frame_{t:05.1f}.png"))
        print("ok")
        sys.exit()
    audio = os.path.join(HERE, "audio.wav")
    print("audio...", flush=True)
    build_audio(audio)
    out = os.path.join(HERE, "what_if_animals_could_talk.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(TOTAL * FPS)
    for i in range(nf):
        p.stdin.write(render(i / FPS).tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{nf}", flush=True)
    p.stdin.close(); p.wait()
    print("done", out)
