#!/usr/bin/env python3
"""What if the Sun turned off right now? — same style as the animals Reel."""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_reel as R
from make_reel import (W, H, FPS, SR, YEL, WHITE, RED, OUTL, CPS, F_TITLE, font, clamp, ease_out,
                       ease_back, comp, paste_c, wrap_words, is_emph, text_sprite, make_bubble,
                       make_clock, grad)

TOTAL = 50.5
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- characters
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1.0):
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))

    def E(b, fill, w=2.6, dd=None):
        dd = dd or d
        x0, y0, x1, y1 = b
        dd.ellipse([x0 * u, y0 * u, x1 * u, y1 * u], fill=fill, outline=OUTL if w else None,
                   width=lw(w) if w else 0)

    def PG(pts, fill, w=2.6):
        d.polygon([(x * u, y * u) for x, y in pts], fill=fill, outline=OUTL if w else None,
                  width=lw(w) if w else 0)

    def LN(pts, w=2.0, fill=OUTL):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")

    def eyes(lx, rx, y, r, closed=False):
        for x in (lx, rx):
            if blink or closed:
                d.arc([(x - r) * u, (y - r * 0.7) * u, (x + r) * u, (y + r * 0.7) * u], 200, 340,
                      fill=OUTL, width=lw(max(2.2, r * 0.27)))
                continue
            E((x - r, y - r * 1.12, x + r, y + r * 1.12), WHITE, w=max(1.6, r * 0.22))
            px, py = x + look[0] * r * 0.38, y + look[1] * r * 0.38
            E((px - r * 0.46, py - r * 0.52, px + r * 0.46, py + r * 0.52), (25, 20, 30), w=0)
            E((px - r * 0.42, py - r * 0.5, px - r * 0.06, py - r * 0.14), WHITE, w=0)

    def mouth(x, y, wd, o, flat=False):
        if flat:
            LN([(x - wd / 2, y), (x + wd / 2, y)], 3); return
        if o > 0.08:
            h = wd * 0.15 + wd * 0.62 * o
            E((x - wd / 2, y - h * 0.3, x + wd / 2, y + h), (125, 28, 48), w=max(1.6, wd * 0.1))
            E((x - wd * 0.3, y + h * 0.35, x + wd * 0.3, y + h * 0.95), (245, 115, 135), w=0)
        else:
            d.arc([(x - wd / 2) * u, (y - wd * 0.3) * u, (x + wd / 2) * u, (y + wd * 0.23) * u], 20, 160,
                  fill=OUTL, width=lw(max(2, wd * 0.11)))

    def cheeks(xl, xr, y, r=8):
        E((xl - r, y - r * 0.6, xl + r, y + r * 0.6), (255, 140, 140), w=0)
        E((xr - r, y - r * 0.6, xr + r, y + r * 0.6), (255, 140, 140), w=0)

    if kind == "sun":
        if state > 0.5:
            rot = T * 25
            for i in range(12):
                a = math.radians(rot + i * 30); a1 = a - math.radians(9); a2 = a + math.radians(9)
                ext = 97 + 4 * math.sin(T * 6 + i)
                PG([(100 + 64 * math.cos(a1), 100 + 64 * math.sin(a1)),
                    (100 + ext * math.cos(a), 100 + ext * math.sin(a)),
                    (100 + 64 * math.cos(a2), 100 + 64 * math.sin(a2))], (255, 158, 40))
            E((32, 32, 168, 168), (255, 212, 60))
            E((50, 46, 120, 90), (255, 232, 130), w=0)
            cheeks(64, 136, 116, 10)
            eyes(78, 122, 92, 12.5)
            mouth(100, 128, 30, talk)
        else:
            E((32, 32, 168, 168), (66, 68, 90))
            E((50, 46, 120, 90), (82, 84, 108), w=0)
            eyes(78, 122, 96, 12.5, closed=True)
            mouth(100, 130, 22, 0, flat=True)
    elif kind == "earth":
        E((30, 30, 170, 170), (70, 150, 240))
        land = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(land)
        g = (98, 192, 112) if state > 0.5 else (236, 244, 255)
        for b in ((40, 48, 96, 100), (104, 36, 150, 70), (108, 102, 168, 154), (50, 122, 86, 160), (130, 64, 172, 96)):
            E(b, g, w=0, dd=ld)
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).ellipse([31 * u, 31 * u, 169 * u, 169 * u], fill=255)
        L.alpha_composite(Image.composite(land, Image.new("RGBA", (S, S), (0, 0, 0, 0)), mask))
        d.ellipse([30 * u, 30 * u, 170 * u, 170 * u], outline=OUTL, width=lw(2.6))
        cheeks(62, 138, 116, 9)
        eyes(78, 122, 92, 12)
        mouth(100, 128, 28, talk)
    elif kind == "flower":
        LN([(100, 200), (100, 112)], 9)
        LN([(100, 198), (100, 112)], 5, fill=(80, 170, 80))
        E((58, 150, 100, 172), (96, 186, 96)); E((100, 138, 142, 160), (96, 186, 96))
        pet = (255, 128, 170)
        for i in range(8):
            a = math.radians(i * 45 + 8 * math.sin(T * 2))
            cx, cy = 100 + 36 * math.cos(a), 76 + 36 * math.sin(a)
            E((cx - 19, cy - 19, cx + 19, cy + 19), pet)
        E((68, 44, 132, 108), (255, 214, 60))
        cheeks(80, 120, 86, 6)
        eyes(88, 112, 70, 7.5)
        mouth(100, 88, 16, talk)
    elif kind == "penguin":
        flap = 10 * talk
        E((66, 182, 98, 198), (250, 150, 50)); E((102, 182, 134, 198), (250, 150, 50))
        E((28, 92 - flap, 60, 162 - flap), (40, 40, 54)); E((140, 92 - flap, 172, 162 - flap), (40, 40, 54))
        E((44, 26, 156, 192), (40, 40, 54))
        E((62, 92, 138, 188), (250, 250, 250), w=0)
        E((58, 40, 142, 112), (250, 250, 250), w=0)
        d.rounded_rectangle([50 * u, 108 * u, 150 * u, 124 * u], radius=8 * u, fill=(222, 60, 64),
                            outline=OUTL, width=lw(2))
        d.rounded_rectangle([118 * u, 114 * u, 136 * u, 150 * u], radius=6 * u, fill=(222, 60, 64),
                            outline=OUTL, width=lw(2))
        cheeks(70, 130, 92, 7)
        eyes(82, 118, 70, 9)
        o = talk
        if o > 0.08:
            PG([(90, 92), (110, 92), (100, 100 + 9 * o)], (222, 128, 40))
        PG([(88, 82), (112, 82), (100, 94 - 2 * o)], (250, 160, 50))
    elif kind == "fish":
        wag = 6 * math.sin(T * 5)
        PG([(150, 100), (192, 62 + wag), (192, 138 + wag)], (250, 150, 70))
        PG([(76, 56), (118, 34), (132, 58)], (250, 150, 70))
        E((22, 52, 166, 148), (255, 192, 84))
        E((98, 58, 116, 142), (255, 156, 64), w=0); E((126, 66, 140, 134), (255, 156, 64), w=0)
        d.ellipse([22 * u, 52 * u, 166 * u, 148 * u], outline=OUTL, width=lw(2.6))
        PG([(96, 110), (124, 120), (100, 132)], (250, 150, 70))
        cheeks(46, 92, 108, 6)
        eyes(52, 82, 86, 10)
        mouth(46, 118, 16, talk)
    elif kind == "worm":
        sway = 4 * math.sin(T * 2.2)
        for cx, cy, r in ((70, 56, 20), (100, 40, 22), (130, 56, 20), (82, 76, 19), (118, 76, 19), (100, 64, 20),
                          (58, 80, 15), (142, 80, 15)):
            E((cx - r + sway, cy - r, cx + r + sway, cy + r), (232, 54, 70))
            E((cx - r * 0.45 + sway, cy - r * 0.6, cx + r * 0.15 + sway, cy), (250, 120, 130), w=0)
        d.rounded_rectangle([70 * u, 86 * u, 130 * u, 204 * u], radius=24 * u, fill=(244, 238, 228),
                            outline=OUTL, width=lw(2.6))
        for y in (162, 178, 192):
            LN([(72, y), (128, y)], 1.6, fill=(196, 188, 176))
        cheeks(82, 118, 136, 6)
        eyes(88, 112, 116, 8)
        mouth(100, 140, 16, talk)
    return L.reduce(2)

# ---------------------------------------------------------------- backgrounds
def stars(d, rng, k, n, ymax, col=(230, 230, 255)):
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, ymax); r = rng.uniform(1.5, 4)
        d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=col)

def build(kind):
    k = 2
    rng = np.random.default_rng(abs(hash(kind)) % 997)
    if kind in ("intro", "outro"):
        return R.build_bg("intro")
    G = {
        "space": [(0, (4, 6, 22)), (1, (22, 14, 54))],
        "day": [(0, (96, 184, 255)), (0.65, (200, 236, 255)), (1, (200, 236, 255))],
        "night": [(0, (2, 2, 10)), (1, (12, 10, 28))],
        "week": [(0, (8, 12, 36)), (1, (44, 54, 96))],
        "year": [(0, (2, 4, 16)), (0.17, (2, 4, 16)), (0.23, (40, 96, 160)), (1, (6, 20, 52))],
        "deep": [(0, (4, 12, 32)), (1, (2, 6, 18))],
    }[kind]
    img = grad(G, W * k, H * k); d = ImageDraw.Draw(img)
    E = lambda b, f: d.ellipse([v * k for v in b], fill=f)
    Rr = lambda b, f, r=0: d.rounded_rectangle([v * k for v in b], radius=r * k, fill=f) if r else d.rectangle([v * k for v in b], fill=f)
    PG = lambda pts, f: d.polygon([(x * k, y * k) for x, y in pts], fill=f)
    LN = lambda pts, f, w: d.line([(x * k, y * k) for x, y in pts], fill=f, width=w * k)

    if kind == "space":
        for cx, cy, r, c in ((250, 500, 380, (30, 20, 70)), (850, 1350, 420, (20, 26, 70))):
            E((cx - r, cy - r, cx + r, cy + r), c)
        stars(d, rng, k, 140, H)
    elif kind in ("day", "night"):
        dark = kind == "night"
        if dark:
            stars(d, rng, k, 160, 1250)
        else:
            for cx, cy in ((240, 560), (820, 760)):
                for dx, r in ((-60, 50), (0, 70), (60, 50)):
                    E((cx + dx - r, cy - r, cx + dx + r, cy + r), WHITE)
            E((110, 330, 190, 410), (236, 240, 250))  # pale daytime moon
        E((-300, 1150, 700, 1560), (40, 70, 52) if dark else (128, 204, 112))
        E((380, 1120, 1400, 1560), (34, 60, 46) if dark else (112, 192, 98))
        Rr((0, 1330, 1080, 1920), (28, 52, 38) if dark else (106, 186, 92))
        for _ in range(50):
            x, y = rng.uniform(0, W), rng.uniform(1360, H)
            PG([(x, y), (x + 8, y - 26), (x + 16, y)], (22, 42, 30) if dark else (86, 164, 74))
    elif kind == "week":
        stars(d, rng, k, 90, 1100)
        for x, sc in ((90, 1.0), (240, 0.8), (860, 1.1), (1000, 0.85)):
            base = 1330
            for j in range(3):
                w_ = (110 - j * 26) * sc; top = base - (90 + j * 70) * sc
                PG([(x - w_, base - j * 60 * sc), (x, top - 40 * sc), (x + w_, base - j * 60 * sc)], (30, 70, 64))
                PG([(x - w_ * 0.45, top + 6 * sc), (x, top - 40 * sc), (x + w_ * 0.45, top + 6 * sc)], (240, 246, 255))
        E((-200, 1260, 600, 1500), (226, 236, 252)); E((400, 1240, 1300, 1500), (214, 228, 250))
        Rr((0, 1330, 1080, 1920), (226, 236, 252))
        for _ in range(30):
            x, y = rng.uniform(0, W), rng.uniform(1380, H)
            E((x - 30, y - 6, x + 30, y + 6), (200, 214, 240))
    elif kind == "year":
        stars(d, rng, k, 60, 320)
        Rr((0, 330, 1080, 450), (214, 236, 250))
        Rr((0, 330, 1080, 350), (240, 250, 255))
        for _ in range(9):
            x = rng.uniform(40, 1040)
            LN([(x, 352), (x + rng.uniform(-40, 40), 400), (x + rng.uniform(-60, 60), 446)], (170, 206, 230), 3)
        for y in range(560, 1900, 160):
            LN([(0, y), (1080, y + 30)], (40, 90, 150), 3)
        Rr((0, 1700, 1080, 1920), (10, 26, 50))
    elif kind == "deep":
        for _ in range(120):
            x, y = rng.uniform(0, W), rng.uniform(0, H); r = rng.uniform(1.5, 3.5)
            E((x - r, y - r, x + r, y + r), (70, 100, 130))
        PG([(0, 1330), (180, 1290), (360, 1340), (560, 1300), (760, 1350), (1080, 1300), (1080, 1920), (0, 1920)], (26, 30, 40))
        PG([(800, 1340), (830, 1080), (860, 960), (900, 950), (930, 1060), (960, 1340)], (60, 50, 50))
        PG([(850, 1100), (870, 1000), (890, 1000), (910, 1100)], (220, 110, 40))
        for x, h, s in ((120, 110, 0.5), (170, 140, 0.6), (220, 100, 0.45), (960, 120, 0.5), (1010, 90, 0.4)):
            Rr((x - 10 * s * 2, 1330 - h, x + 10 * s * 2, 1336), (230, 224, 214), 10)
            E((x - 18 * s * 2, 1330 - h - 26 * s * 2, x + 18 * s * 2, 1330 - h + 10 * s * 2), (210, 50, 64))
    return img.reduce(k)

# ---------------------------------------------------------------- script
OFF_AT = 6.6       # sun switches off (scene 2)
TRAVEL = (10.8, 16.0)   # 0:00 -> 8:20 counter
BLACKOUT = 18.6
SCENES = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="sunoff", s=4.0, e=10.5, bg="space", clock="0:00", char="sun",
         say="Okay, I'm OUT.", say_at=5.0, pitch=420,
         narr="The Sun switches off. On Earth? NOTHING happens.", n_at=7.0),
    dict(id="travel", s=10.5, e=17.0, bg="space", clock=None, char="earth",
         say="Feels totally normal to me.", say_at=12.2, pitch=260,
         narr="The last sunlight takes 8 min 20 sec to reach us.", n_at=10.7),
    dict(id="blackout", s=17.0, e=24.5, bg="day", clock="8 MIN 20 SEC", char="flower",
         say="Hey! Who turned off the LIGHTS?!", say_at=20.0, pitch=700, look=(0, -0.4),
         narr="Then the sky goes BLACK. Even the Moon vanishes.", n_at=18.9),
    dict(id="week", s=24.5, e=31.5, bg="week", clock="1 WEEK LATER", char="penguin",
         say="Finally. MY kind of weather.", say_at=25.9, pitch=560,
         narr="Temperatures crash below -18°C.", n_at=24.7),
    dict(id="year", s=31.5, e=38.5, bg="year", clock="1 YEAR LATER", char="fish",
         say="Ice roof up top. The water down here stays LIQUID.", say_at=32.8, pitch=480, look=(0, -0.3),
         narr="About -73°C. The oceans freeze over.", n_at=31.7),
    dict(id="deep", s=38.5, e=45.5, bg="deep", clock="DEEP SEA", char="worm", enter=39.7,
         say="Wait... you guys NEEDED the Sun?", say_at=41.0, pitch=150,
         narr="But deep down, some life keeps GOING.", n_at=38.8),
    dict(id="outro", s=45.5, e=50.5),
]
for sc in SCENES:
    if "say" in sc:
        sc["say_end"] = sc["say_at"] + len(sc["say"]) * CPS
PUNCH = 43.0

# ---------------------------------------------------------------- assets
print("sun assets...", flush=True)
BGS = {k: build(k) for k in ("intro", "space", "day", "night", "week", "year", "deep")}
SUNGLOW = R.glow_sun(260)
BUB = {sc["id"]: make_bubble(sc["say"]) for sc in SCENES if "say" in sc}
_clk = {}
def clock_spr(label):
    if label not in _clk:
        _clk[label] = make_clock(label)
    return _clk[label]
T_WHATIF = text_sprite([("WHAT IF", YEL)], 220)
T_L2 = text_sprite([("THE SUN", WHITE)], 140)
T_L3 = text_sprite([("TURNED OFF", WHITE)], 140)
T_L4 = text_sprite([("...right ", WHITE), ("NOW?", YEL)], 90)
T_O1 = text_sprite([("Would ", WHITE), ("YOU", YEL), (" survive", WHITE)], 96)
T_O2 = text_sprite([("the dark?", YEL)], 120)
T_FOLLOW = text_sprite([("Follow ", WHITE), ("@whatif.wala", YEL)], 58, stroke=7)
T_COMMENT = R.T_COMMENT
T_LAST = text_sprite([("LAST SUNLIGHT", YEL)], 40, path=R.F_CAP, stroke=5, shadow=False)

def blink_at(T, seed): return ((T * 0.37 + seed) % 1.0) < 0.045
def talk_amt(sc, T):
    if "say" in sc and sc["say_at"] <= T < sc["say_end"]:
        return clamp(0.5 + 0.55 * math.sin(T * 27))
    return 0.0

def scene_at(T):
    for sc in SCENES:
        if sc["s"] <= T < sc["e"]:
            return sc
    return SCENES[-1]

def draw_narr(frame, sc, T):
    if "narr" not in sc or T < sc["n_at"]:
        return
    d = ImageDraw.Draw(frame); f = font(66)
    lines = wrap_words(sc["narr"].split(), f, 880)
    n = int((T - sc["n_at"]) / 0.2) + 1
    lh = 86; y0 = 1470 - len(lines) * lh / 2; idx = 0; GAP = 12
    for li, line in enumerate(lines):
        x = 540 - (f.getlength(" ".join(line)) + GAP * (len(line) - 1)) / 2; y = y0 + li * lh
        for w in line:
            if idx < n:
                age = T - (sc["n_at"] + idx * 0.2)
                dy = -14 * (1 - ease_out(age / 0.15))
                emph = is_emph(w) or w.startswith("-")
                d.text((x, y + dy), w, font=f, fill=YEL if emph else WHITE, stroke_width=8, stroke_fill=(0, 0, 0))
            x += f.getlength(w + " ") + GAP; idx += 1

def draw_bubble(frame, sc, T, anchor_y=800):
    if "say" not in sc: return
    t0 = sc["say_at"] - 0.25
    if T < t0: return
    B = BUB[sc["id"]]; b = B["img"].copy(); bd = ImageDraw.Draw(b); f = font(58)
    nvis = int((T - sc["say_at"]) / CPS) + 1 if T >= sc["say_at"] else 0
    count = 0
    for li, line in enumerate(B["lines"]):
        x = (B["bw"] - f.getlength(" ".join(line))) / 2; y = B["pad"] - 6 + li * B["lh"]
        for w in line:
            vis = w[:max(0, nvis - count)]
            if vis:
                bd.text((x, y), vis, font=f, fill=RED if is_emph(w) else (36, 26, 46))
            x += f.getlength(w + " "); count += len(w) + 1
    s = 0.35 + 0.65 * ease_back((T - t0) / 0.3)
    bb = b.resize((max(1, int(b.width * s)), max(1, int(b.height * s))), Image.BILINEAR) if abs(s - 1) > 0.01 else b
    comp(frame, bb, 540 - B["bw"] * s / 2, anchor_y + 60 - bb.height)

def draw_clock(frame, sc, T):
    if sc["id"] in ("intro", "outro"): return
    lt = T - sc["s"] - 0.25
    if lt < 0: return
    if sc["id"] == "travel":
        p = clamp((T - TRAVEL[0]) / (TRAVEL[1] - TRAVEL[0]))
        secs = int(round(p * 500)); label = f"{secs // 60}:{secs % 60:02d}"
    else:
        label = sc["clock"]
    c = clock_spr(label)
    y = 228 - 60 * (1 - ease_back(lt / 0.35))
    comp(frame, c, 540 - c.width / 2, y)

def sun_state(T):
    """1 = on, 0 = off, with a flicker before switching off."""
    if T < OFF_AT - 0.35: return 1
    if T >= OFF_AT: return 0
    return 1 if int((T - OFF_AT) * 20) % 2 == 0 else 0

def render(T):
    sc = scene_at(T); lt = T - sc["s"]; sid = sc["id"]
    if sid == "blackout" and T >= BLACKOUT:
        frame = BGS["night"].copy()
    else:
        frame = BGS[sc.get("bg", "intro")].copy()
    d = ImageDraw.Draw(frame)

    if sid == "intro":
        if T >= 0.2: paste_c(frame, T_WHATIF, 540, 560, 0.2 + 0.8 * ease_back((T - 0.2) / 0.35))
        if T >= 0.75: paste_c(frame, T_L2, 540 + 600 * (1 - ease_out((T - 0.75) / 0.3)), 770)
        if T >= 1.05: paste_c(frame, T_L3, 540 - 600 * (1 - ease_out((T - 1.05) / 0.3)), 915)
        if T >= 1.5: paste_c(frame, T_L4, 540, 1060, 0.3 + 0.7 * ease_back((T - 1.5) / 0.3))
        if T >= 1.9:
            on = 1 if T < 3.1 else (0 if T >= 3.35 else (1 if int(T * 20) % 2 == 0 else 0))
            p = ease_back((T - 1.9) / 0.4)
            if on: paste_c(frame, SUNGLOW, 540, 1380, 0.75 * p)
            spr = draw_char("sun", 400, T, 0, False, (0, 0), on)
            paste_c(frame, spr, 540, 1380, p)
    elif sid == "outro":
        if lt >= 0.15: paste_c(frame, T_O1, 540, 470, 0.3 + 0.7 * ease_back((lt - 0.15) / 0.3))
        if lt >= 0.45:
            paste_c(frame, T_O2, 540, 600, (0.3 + 0.7 * ease_back((lt - 0.45) / 0.3)) * (1 + 0.03 * math.sin(T * 6)))
        row = [("sun", 0), ("earth", 1), ("flower", 1), ("penguin", 1), ("worm", 1)]
        for i, (kd, st) in enumerate(row):
            s0 = 0.9 + i * 0.18
            if lt < s0: continue
            p = ease_back((lt - s0) / 0.35)
            x = 540 + (i - 2) * 205; y = 940 + 300 * (1 - p) + 10 * math.sin(T * 4 + i)
            talk = clamp(0.5 + 0.6 * math.sin(T * 22 + i * 2)) if 1.8 <= lt < 3.4 else 0
            comp(frame, draw_char(kd, 200, T, talk, blink_at(T, i * 0.2), (0, 0.2), st), x - 100, y - 100)
        if lt >= 2.2:
            paste_c(frame, T_COMMENT, 540, 1235, (0.3 + 0.7 * ease_back((lt - 2.2) / 0.3)) * (1 + 0.04 * math.sin(T * 7)))
            ay = 1360 + 18 * abs(math.sin(T * 5))
            d.polygon([(500, ay), (580, ay), (540, ay + 60)], fill=WHITE, outline=OUTL, width=5)
        if lt >= 2.6:
            paste_c(frame, T_FOLLOW, 540, 1530, 0.3 + 0.7 * ease_back((lt - 2.6) / 0.3))
    else:
        enter = sc.get("enter", sc["s"] + 0.15)
        talk = talk_amt(sc, T)
        look = sc.get("look", (0, 0.15))
        cx, cy, B = 540, 1080, 600

        # scene props behind the character
        if sid == "travel":
            # dim, switched-off sun far away on the left
            comp(frame, draw_char("sun", 200, T, 0, False, (0, 0), 0), -60, 560)
            p = clamp((T - TRAVEL[0]) / (TRAVEL[1] - TRAVEL[0]))
            if TRAVEL[0] <= T < TRAVEL[1] + 0.25:
                px = -60 + (360 - -60) * p
                for j in range(14):
                    tx = px - j * 26; r = 26 - j * 1.6
                    if r > 2:
                        c = (255, 220 - j * 6, 90 + j * 4)
                        d.ellipse([tx - r, 1080 - r, tx + r, 1080 + r], fill=c)
                d.ellipse([px - 34, 1046, px + 34, 1114], fill=(255, 250, 210), outline=(255, 190, 60), width=6)
                comp(frame, T_LAST, px - T_LAST.width / 2 + 40, 965)
        if sid == "week":
            for j in range(40):
                sx = (j * 137.5 + 40 * math.sin(T * 0.8 + j)) % W
                sy = (j * 211 + T * (90 + (j % 5) * 25)) % 1400
                r = 4 + (j % 3) * 2
                d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(240, 246, 255))
        if sid == "deep":
            for j in range(9):
                ph = (T * 0.35 + j / 9) % 1.0
                r = 22 + 60 * ph
                gx = 880 + 30 * math.sin(j * 2.1 + T) * ph
                gy = 950 - 520 * ph
                g = int(70 - 40 * ph)
                d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(g, g - 6, g - 10))

        if sid == "sunoff":
            B = 680
            if T >= enter and sun_state(T): paste_c(frame, SUNGLOW, cx, cy, 1.15 * ease_back((T - enter) / 0.55))
        if sid == "travel":
            cx = 560
        if sid == "year":
            cx = 540 + 40 * math.sin(T * 0.9); cy = 1060 + 14 * math.sin(T * 1.7)
            for j in range(6):
                ph = (T * 0.6 + j / 6) % 1.0
                bx = cx - 230 + 12 * math.sin(T * 3 + j); by = cy + 40 - 520 * ph; r = 8 + 10 * ph
                if by > 460:
                    d.ellipse([bx - r, by - r, bx + r, by + r], outline=(180, 220, 255), width=4)

        if T >= enter:
            le = T - enter
            p = ease_back(le / 0.55)
            bob = 8 * math.sin(T * 3.2) + (6 * math.sin(T * 20) if talk > 0 else 0)
            y = cy + 640 * (1 - p) + bob
            state = sun_state(T) if sid == "sunoff" else 1
            if sid == "travel":
                state = 1
            spr = draw_char(sc["char"], B, T, talk, blink_at(T, 0.5), look, state)
            comp(frame, spr, cx - B / 2, y - B / 2)
        draw_bubble(frame, sc, T)

        # blackout: hard cut to black, then the night fades in
        if sid == "blackout" and BLACKOUT <= T < BLACKOUT + 0.9:
            a = 1.0 if T < BLACKOUT + 0.35 else 1 - (T - BLACKOUT - 0.35) / 0.55
            frame = Image.blend(frame, Image.new("RGBA", (W, H), (0, 0, 0, 255)), clamp(a))
        if sid == "sunoff" and OFF_AT <= T < OFF_AT + 0.5:
            # brief darkening pulse when the sun dies
            frame = Image.blend(frame, Image.new("RGBA", (W, H), (0, 0, 0, 255)), 0.55 * (1 - (T - OFF_AT) / 0.5))

    draw_clock(frame, sc, T)
    draw_narr(frame, sc, T)

    if sid != "intro" and lt < 0.2:
        s = 1.0 + 0.07 * (1 - ease_out(lt / 0.2))
        big = frame.resize((int(W * s), int(H * s)), Image.BILINEAR)
        ox, oy = (big.width - W) // 2, (big.height - H) // 2
        frame = big.crop((ox, oy, ox + W, oy + H))
        if lt < 0.12:
            frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.55 * (1 - lt / 0.12))
    if T < 0.2:
        frame = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), frame, T / 0.2)
    return frame.convert("RGB")

# ---------------------------------------------------------------- audio
def build_audio(path):
    N = int(SR * (TOTAL + 1))
    music = np.zeros(N); fx = np.zeros(N)
    rng = np.random.default_rng(11)
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

    def kick():
        t = tarr(0.35); f = 45 + 110 * np.exp(-t * 22); return np.sin(osc(f)) * np.exp(-t * 9)
    def clap():
        t = tarr(0.18); n = rng.standard_normal(len(t)); n = n - lp(n, 8); return n * np.exp(-t * 28) * 0.5
    def hat():
        t = tarr(0.05); n = rng.standard_normal(len(t)); n = n - lp(n, 3); return n * np.exp(-t * 90) * 0.25
    def pluck(f, dd=0.32):
        t = tarr(dd); ph = 2 * np.pi * f * t
        s = np.sin(ph) + 0.5 * np.sin(2 * ph) * np.exp(-t * 6) + 0.25 * np.sin(3 * ph) * np.exp(-t * 10)
        return fadeout(s * np.minimum(1, t / 0.003) * np.exp(-t * 9))
    def bassn(f, dd=0.45):
        t = tarr(dd); ph = 2 * np.pi * f * t; tri = 2 / np.pi * np.arcsin(np.sin(ph))
        return fadeout((0.7 * tri + 0.5 * np.sin(ph)) * np.minimum(1, t / 0.004) * np.exp(-t * 4.5))
    def bell(f, dd=0.4):
        t = tarr(dd); s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 8)
        return fadeout(s * np.minimum(1, t / 0.002) * np.exp(-t * 7))

    beat = 60 / 112
    MAJ = ([48, 43, 45, 41], [(60, 64, 67), (59, 62, 67), (57, 60, 64), (57, 60, 65)])
    MIN = ([45, 41, 48, 43], [(57, 60, 64), (57, 60, 65), (55, 60, 64), (55, 59, 62)])
    mel = [[(0, 76), (1, 79), (1.5, 76), (2.5, 72), (3, 74)], [(0, 74), (1, 71), (1.5, 74), (2.5, 79), (3, 77)],
           [(0, 76), (1, 72), (1.5, 76), (2.5, 81), (3, 79)], [(0, 77), (1, 76), (1.5, 74), (2.5, 72), (3, 71)]]
    def groove(t0, t1, prog=MAJ, drums=True, clap_on=True, melody=False, g=1.0):
        roots, chords = prog; b = 0
        while True:
            t = t0 + b * beat
            if t >= t1 - 0.05: break
            bar = (b // 4) % 4; pos = b % 4
            if drums:
                if pos in (0, 2) and (clap_on or pos == 0): add(music, kick(), t, 0.85 * g)
                if clap_on and pos in (1, 3): add(music, clap(), t, 0.45 * g)
                add(music, hat(), t + beat / 2, 0.6 * g); add(music, hat(), t, 0.3 * g)
            add(music, bassn(mf(roots[bar])), t, 0.5 * g)
            for m in chords[bar]: add(music, pluck(mf(m)), t + beat / 2, 0.13 * g)
            if melody and pos == 0:
                for off, m in mel[bar]:
                    if t + off * beat < t1 - 0.05: add(music, bell(mf(m)), t + off * beat, 0.16 * g)
            b += 1

    groove(0.2, 4.0, drums=False)
    groove(4.0, BLACKOUT, drums=True)
    groove(BLACKOUT + 1.0, 38.4, prog=MIN, drums=True, clap_on=False, g=0.9)
    groove(45.5, TOTAL, drums=True, melody=True)
    # deep-sea drone
    t = tarr(7.2); env = np.minimum(1, t / 1.2) * np.minimum(1, (7.2 - t) / 0.6)
    drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t) + 0.3 * np.sin(2 * np.pi * 110 * t)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.4 * t))
    add(music, drone * env * 0.12, 38.5)

    def whoosh(dd=0.45):
        t = tarr(dd); n = rng.standard_normal(len(t)); env = np.sin(np.pi * t / dd) ** 2
        return (lp(n, 14) * 1.3 + 0.25 * (n - lp(n, 4)) * (t / dd)) * env * 0.45
    def boom():
        t = tarr(1.4); f = 38 + 60 * np.exp(-t * 6)
        return (np.sin(osc(f)) * np.exp(-t * 3) + lp(rng.standard_normal(len(t)), 20) * np.exp(-t * 12) * 0.6) * 0.9
    def pop():
        t = tarr(0.09); f = 500 + 900 * t / 0.09; return np.sin(osc(f)) * np.sin(np.pi * t / 0.09) * 0.45
    def tick(f=2200):
        t = tarr(0.05); return np.sin(2 * np.pi * f * t) * np.exp(-t * 150) * 0.45
    def click():
        t = tarr(0.12); s = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 300) + np.sin(2 * np.pi * 120 * t) * np.exp(-t * 40) * 0.8
        return s * 0.7
    def powerdown(dd=1.3):
        t = tarr(dd); f = 520 * np.exp(-t * 2.6) + 30; ph = osc(f)
        s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
        return s * np.minimum(1, t / 0.01) * (1 - t / dd) ** 1.5 * 0.45
    def shimmer():
        t = tarr(0.9); s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (3 + i)) for i, f in enumerate((1568, 2093, 2637, 3136)))
        return s * np.minimum(1, t / 0.01) * 0.18
    def blip(f, g=1.0):
        t = tarr(0.055); ff = f * (1 + 0.25 * np.exp(-t * 80)); ph = osc(ff)
        s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph)
        return fadeout(s * np.minimum(1, t / 0.004) * np.exp(-t * 30) * 0.26 * g)
    def babble(text, t0, base, g=1.0, cps=CPS):
        for i, ch in enumerate(text):
            if ch.isalnum():
                f = base * 2 ** ((((ord(ch.lower()) * 5) % 9) - 4) / 14)
                add(fx, blip(f, 1.3 if ch.isupper() else 1.0), t0 + i * cps, g)
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
    def wind(dd):
        t = tarr(dd); n = rng.standard_normal(len(t))
        s = lp(n, 30) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t) ** 2)
        whistle = np.sin(osc(650 + 120 * np.sin(2 * np.pi * 0.3 * t))) * 0.05 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.22 * t))
        return (s * 2.2 + whistle) * np.minimum(1, t / 0.6) * np.minimum(1, (dd - t) / 0.4) * 0.35
    def bubbles(dd):
        s = np.zeros(int(dd * SR))
        for _ in range(int(dd * 3)):
            t0 = rng.uniform(0, dd - 0.1); t = tarr(0.07); f = rng.uniform(300, 600) * (1 + 2 * t / 0.07)
            sig = np.sin(osc(f)) * np.sin(np.pi * t / 0.07) * 0.25
            i = int(t0 * SR); s[i:i + len(sig)] += sig
        return s
    def crack():
        t = tarr(0.35); n = rng.standard_normal(len(t)); n = n - lp(n, 2)
        s = n * np.exp(-t * 18)
        for _ in range(6):
            i = int(rng.uniform(0, 0.25) * SR); s[i:i + 200] += rng.standard_normal(200) * 0.8
        return s * 0.45
    def underwater(dd):
        t = tarr(dd); return lp(rng.standard_normal(len(t)), 300) * 3.0 * np.minimum(1, t / 0.5) * np.minimum(1, (dd - t) / 0.5)

    # intro
    add(fx, boom(), 0.2); add(fx, pop(), 0.75); add(fx, pop(), 1.05); add(fx, pop(), 1.5, 1.2); add(fx, pop(), 1.9)
    add(fx, click(), 3.35); add(fx, powerdown(0.9), 3.36, 0.8)
    for sc in SCENES[1:]:
        add(fx, whoosh(), sc["s"] - 0.2)
        if sc["id"] not in ("outro",): add(fx, tick(), sc["s"] + 0.25)
    # sun switches off
    add(fx, click(), OFF_AT); add(fx, powerdown(), OFF_AT + 0.01)
    # 8:20 counter ticks + arrival
    t = TRAVEL[0]
    while t < TRAVEL[1]:
        add(fx, tick(2600), t, 0.6); t += 0.13
    add(fx, shimmer(), TRAVEL[1])
    # blackout
    add(fx, click(), BLACKOUT, 1.3); add(fx, boom(), BLACKOUT, 0.8); add(fx, powerdown(1.0), BLACKOUT, 0.7)
    # week
    add(fx, wind(7.0), 24.5)
    add(fx, babble("kwak kwak", 24.75, 620, 0.7, 0.05) if False else np.zeros(1), 0)
    for i, c in enumerate("kwakwak"):
        add(fx, blip(640 * 2 ** ((i % 3) / 12), 1.1), 24.75 + i * 0.07)
    # year
    add(fx, crack(), 31.6); add(fx, crack(), 32.3, 0.6)
    add(fx, underwater(7.0), 31.5, 0.6); add(fx, bubbles(6.8), 31.6)
    # deep
    add(fx, scratch(), 38.35)
    add(fx, pop(), 39.75)
    add(fx, ding(), PUNCH)
    # outro
    add(fx, boom(), 45.55, 0.6)
    for i in range(5): add(fx, pop(), 45.5 + 0.9 + i * 0.18)
    add(fx, pop(), 47.7, 1.2); add(fx, ding(1760), 49.3, 0.6)
    for sc in SCENES:
        if "say" in sc: babble(sc["say"], sc["say_at"], sc["pitch"], 1.0)

    gain = np.full(N, 0.6)
    for sc in SCENES:
        if "say" in sc:
            gain[int((sc["say_at"] - 0.2) * SR):int((sc["say_end"] + 0.2) * SR)] = 0.33
    gain = lp(gain, int(0.15 * SR))
    tot = np.arange(N) / SR
    gain *= np.clip((TOTAL - tot) / 0.8, 0, 1)
    mix = music * gain + fx * np.clip((TOTAL + 0.05 - tot) / 0.3, 0, 1)
    mix = np.tanh(mix * 1.2); mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.9
    pcm = (mix[:int(TOTAL * SR)] * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], 1).reshape(-1).tobytes())

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "preview":
        times = [float(x) for x in sys.argv[2].split(",")]
        frames = [render(t) for t in times]
        tw_, th_ = 270, 480; cols = 4; rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw_, rows * th_))
        for i, fr in enumerate(frames):
            sheet.paste(fr.resize((tw_, th_)), ((i % cols) * tw_, (i // cols) * th_))
        sheet.save(os.path.join(HERE, "sun_preview.png")); print("ok"); sys.exit()
    audio = os.path.join(HERE, "sun_audio.wav")
    build_audio(audio)
    out = os.path.join(HERE, "what_if_the_sun_turned_off.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(TOTAL * FPS)
    for i in range(nf):
        p.stdin.write(render(i / FPS).tobytes())
        if i % 300 == 0: print(f"frame {i}/{nf}", flush=True)
    p.stdin.close(); p.wait(); print("done", out)
