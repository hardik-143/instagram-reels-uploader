#!/usr/bin/env python3
"""What if your voice kept getting louder? A decibel ladder. Whisper ~30 dB, normal talk 60-70 dB, 85 dBA can damage
hearing after 8 hours, 110 dBA after 2 minutes, ambulance sirens 110-129 dBA, jet taking off 140 dBA (NIH/NIDCD
"How loud is too loud"). India's firecracker limit: 125 dB(AI) measured 4 m from the burst point (Environment
Protection Rules / Supreme Court; Open magazine 2026 explainer: no change in force). +10 dB ~ sounds twice as loud
(standard psychoacoustics rule of thumb). Krakatoa, 27 Aug 1883: ~172 dB recorded at Batavia gasworks 160 km away
(Bruel & Kjaer); heard on Rodrigues island ~4,800 km away about 4 hours later; pressure wave circled Earth ~7 times
(Oregon State Volcano World). Twist: in Earth's air a sound wave can't swing below vacuum, so ~194 dB is the
ceiling; beyond that it becomes a shock wave (Science ABC). Safety: noise damage is permanent; keep back from crackers."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 56.0   # twist start

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=56, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

_gl = {}
def glow(frame, x, y, r, col=(255, 200, 120), s=0.8):
    k = (int(r), col, round(s, 2))
    if k not in _gl:
        R = max(2, int(r))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        q = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / R, 0, 1) ** 2
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (q * 255 * s).astype(np.uint8)
        _gl[k] = Image.fromarray(arr, "RGBA")
    g = _gl[k]
    frame.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

# ---------------------------------------------------------------- decibel meter on the left edge
LEVELS = {"whisper": 30, "talk": 60, "traffic": 85, "siren": 110, "cracker": 125, "jet": 140, "krakatoa": 172,
          "wave": 172, "twist": 194}
ORDER = list(LEVELS)
TOPDB = 200.0

def meter(frame, d, T, sc):
    lt = T - sc["s"]
    i = ORDER.index(sc["id"])
    prev = LEVELS[ORDER[i - 1]] if i else 0
    lv = prev + (LEVELS[sc["id"]] - prev) * ease_out(clamp(lt / 1.2))
    x, top, bot = 80, 470, 1220
    d.rounded_rectangle([x - 34, top - 10, x + 34, bot + 10], 20, fill=(40, 40, 50), outline=OUTL, width=5)
    n = 20
    for k in range(n):
        db = (k + 0.5) / n * TOPDB
        y1 = bot - (bot - top) * k / n; y0 = bot - (bot - top) * (k + 1) / n + 6
        if db <= lv:
            col = (90, 210, 110) if db < 85 else (255, 210, 60) if db < 120 else (240, 70, 60)
        else:
            col = (80, 80, 92)
        d.rectangle([x - 22, y0, x + 22, y1], fill=col)
    put_label(frame, "dB", x, top - 90, 44, WHITE)

def with_meter(fn=None):
    def p(frame, d, T, sc):
        if fn: fn(frame, d, T, sc)
        meter(frame, d, T, sc)
    return p

def arcs(d, x, y, T, n=3, r0=60, step=50, col=WHITE, width=10, spd=1.4, spread=50, ang=0):
    for k in range(n):
        ph = (T * spd + k / n) % 1.0
        r = r0 + step * n * ph
        a = int(255 * (1 - ph))
        bb = [x - r, y - r, x + r, y + r]
        d.arc(bb, ang - spread, ang + spread, fill=OUTL, width=width + 6)
        d.arc(bb, ang - spread, ang + spread, fill=col, width=width)

# ---------------------------------------------------------------- scene props
def whisper_props(frame, d, T, sc):
    comp(frame, draw_char("cat", 300, T, 0, True, (0, 0), 1), 640, 1000)
    arcs(d, 560, 960, T, n=2, r0=40, step=30, col=(200, 220, 255), width=5, spd=0.8, spread=30)
    put_label(frame, "zzz", 860, 930, 48, WHITE)

def talk_props(frame, d, T, sc):
    arcs(d, 640, 960, T, n=3, r0=50, step=45, col=WHITE, width=8, spd=1.0, spread=40)

def traffic_props(frame, d, T, sc):
    arcs(d, 760, 1000, T, n=3, r0=60, step=55, col=(255, 230, 120), width=10, spd=1.6, spread=45)

def ambulance(d, cx, cy, T):
    d.rounded_rectangle([cx - 230, cy - 120, cx + 230, cy + 110], 30, fill=WHITE, outline=OUTL, width=6)
    d.rectangle([cx - 230, cy - 10, cx + 230, cy + 30], fill=(230, 60, 60))
    d.rectangle([cx - 30, cy - 95, cx + 30, cy - 35], fill=(230, 60, 60))
    d.rectangle([cx - 55, cy - 75, cx + 55, cy - 55], fill=(230, 60, 60))
    d.rounded_rectangle([cx + 90, cy - 100, cx + 210, cy - 20], 14, fill=(170, 220, 250), outline=OUTL, width=5)
    for wx in (cx - 140, cx + 140):
        d.ellipse([wx - 50, cy + 70, wx + 50, cy + 170], fill=(50, 50, 60), outline=OUTL, width=5)
        d.ellipse([wx - 20, cy + 100, wx + 20, cy + 140], fill=(180, 180, 190))
    on = (T % 0.5) < 0.25
    d.rounded_rectangle([cx - 60, cy - 160, cx - 5, cy - 120], 10, fill=(255, 60, 60) if on else (120, 30, 30),
                        outline=OUTL, width=4)
    d.rounded_rectangle([cx + 5, cy - 160, cx + 60, cy - 120], 10, fill=(60, 120, 255) if not on else (30, 50, 120),
                        outline=OUTL, width=4)

def siren_props(frame, d, T, sc):
    ambulance(d, 600, 1110, T)
    arcs(d, 600, 950, T, n=3, r0=60, step=40, col=(255, 120, 120), width=10, spd=2.0, spread=35, ang=-90)
    lt = T - sc["s"]
    if lt > 2.0: put_label(frame, "DAMAGE IN 2 MIN", 600, 680, 56)

def cracker_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 760, 1050
    d.rounded_rectangle([cx - 50, cy - 130, cx + 50, cy + 60], 18, fill=(220, 50, 50), outline=OUTL, width=6)
    d.rectangle([cx - 50, cy - 60, cx + 50, cy - 30], fill=(255, 210, 60))
    d.line([(cx, cy - 130), (cx + 20, cy - 190)], fill=OUTL, width=6)
    if (lt % 2.0) < 1.0:
        for k in range(8):
            a = k * math.pi / 4 + lt * 10
            d.line([(cx + 20, cy - 190), (cx + 20 + 34 * math.cos(a), cy - 190 + 34 * math.sin(a))],
                   fill=(255, 220, 80), width=5)
    # 4 m distance marker
    d.line([(430, 1190), (760, 1190)], fill=WHITE, width=6)
    for x in (430, 760):
        d.line([(x, 1165), (x, 1215)], fill=WHITE, width=6)
    put_label(frame, "4 METRES", 595, 1205, 44, WHITE)

def jet(d, cx, cy, s=1.0):
    P = lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]
    d.polygon(P([(-80, -40), (40, -150), (90, -150), (30, -30)]), fill=(200, 205, 220), outline=OUTL)
    d.polygon(P([(-80, 40), (40, 150), (90, 150), (30, 30)]), fill=(180, 185, 200), outline=OUTL)
    d.rounded_rectangle([cx - 260 * s, cy - 45 * s, cx + 260 * s, cy + 45 * s], int(45 * s), fill=(240, 242, 250),
                        outline=OUTL, width=6)
    d.polygon(P([(-250, -30), (-290, -130), (-220, -130), (-180, -30)]), fill=(80, 140, 230), outline=OUTL)
    for k in range(5):
        x = cx + (-120 + k * 60) * s
        d.ellipse([x - 14 * s, cy - 22 * s, x + 14 * s, cy - 2 * s], fill=(120, 180, 240))

def jet_props(frame, d, T, sc):
    lt = T - sc["s"]
    x = 620 + 30 * math.sin(lt * 0.8); y = 1080 - 50 * ease_out(clamp(lt / 6))
    for k in range(4):
        ph = (lt * 3 + k / 4) % 1.0
        d.ellipse([x - 300 - 120 * ph - 40, y - 30 + 20 * ph, x - 300 - 120 * ph + 40, y + 50 + 20 * ph],
                  fill=(230, 230, 235), outline=OUTL, width=3)
    jet(d, x, y, 1.0)
    arcs(d, x - 280, y, T, n=3, r0=60, step=45, col=(255, 200, 120), width=12, spd=2.2, spread=35, ang=180)
    if lt > 2.5: put_label(frame, "PAIN ZONE", 620, 820, 60)

def volcano_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.polygon([(220, 1350), (470, 900), (650, 900), (900, 1350)], fill=(100, 70, 60), outline=OUTL)
    glow(frame, 560, 880, 260, (255, 140, 60), 0.9)
    for k in range(7):
        ph = (lt * 0.6 + k / 7) % 1.0
        x = 560 + (k - 3) * 40 * (1 + ph); y = 880 - ph * 380
        r = 30 + 50 * ph
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 110, 110), outline=OUTL, width=4)
    if lt > 0.6:
        q = (lt - 0.6) % 2.0 / 2.0
        r = 100 + 500 * q
        d.ellipse([560 - r, 880 - r, 560 + r, 880 + r], outline=WHITE, width=8)

def wave_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 560, 1060
    for k in range(3):
        ph = (lt * 0.5 + k / 3) % 1.0
        r = 270 + 30 * math.sin(ph * math.pi)
        a = ph * 2 * math.pi
        d.arc([cx - r, cy - r, cx + r, cy + r], math.degrees(a) - 40, math.degrees(a) + 40, fill=WHITE, width=12)
    if lt > 2.6: put_label(frame, "4,800 KM AWAY", 560, 640, 58)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = (lt % 1.6) / 1.6
    r = 120 + 300 * q
    d.ellipse([540 - r, 1080 - r, 540 + r, 1080 + r], outline=(255, 255, 255), width=int(30 * (1 - q)) + 4)
    if lt > 2.8: put_label(frame, "MAX: ~194 dB", 560, 795, 64)

def safety_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k, (x, y) in enumerate(((760, 520), (900, 640), (640, 600))):
        ph = (lt * 0.7 + k * 0.33) % 1.0
        r = 40 + 80 * ph
        for j in range(8):
            a = j * math.pi / 4
            d.line([(x + r * 0.4 * math.cos(a), y + r * 0.4 * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))],
                   fill=[(255, 200, 80), (255, 120, 160), (120, 220, 255)][k], width=6)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="whisper", s=4.0, e=10.5, bg="bedroom", clock="30 dB", char="kid", pos=(470, 1080, 400),
         props=with_meter(whisper_props), look=(0.5, 0.2),
         narr="Start with a WHISPER: about 30 DECIBELS. Even the cat sleeps on.", n_at=4.2,
         say="Psst... SECRET!", say_at=7.0, pitch=600),
    dict(id="talk", s=10.5, e=17.0, bg="living", clock="60 dB", char="kid", pos=(480, 1080, 420),
         props=with_meter(talk_props), look=(0.4, 0),
         narr="Normal TALK: about 60 dB. Every +10 dB sounds about TWICE as loud.", n_at=10.7,
         say="Hello, EVERYONE!", say_at=13.3, pitch=620),
    dict(id="traffic", s=17.0, e=23.5, bg="gully", clock="85 dB", char="auto", pos=(500, 1080, 460),
         props=with_meter(traffic_props), look=(0.4, 0),
         narr="85 dB: busy TRAFFIC. 8 HOURS of this can damage your hearing.", n_at=17.2,
         say="Peep PEEP PEEP!", say_at=19.8, pitch=520),
    dict(id="siren", s=23.5, e=30.0, bg="day", clock="110 dB", props=with_meter(siren_props),
         narr="110 dB: an ambulance SIREN up close. Damage can start in 2 MINUTES.", n_at=23.7),
    dict(id="cracker", s=30.0, e=36.5, bg="diwali", clock="125 dB", char="kid", pos=(300, 1080, 300),
         props=with_meter(cracker_props), look=(0.6, 0),
         narr="125 dB: India's LEGAL limit for one firecracker, measured 4 METRES away.", n_at=30.2,
         say="Standing BACK!", say_at=32.8, pitch=620),
    dict(id="jet", s=36.5, e=43.0, bg="speed", clock="140 dB", props=with_meter(jet_props),
         narr="140 dB: a JET taking off. Now sound doesn't just annoy. It HURTS.", n_at=36.7),
    dict(id="krakatoa", s=43.0, e=49.5, bg="night", clock="172 dB", props=with_meter(volcano_props),
         narr="1883: Krakatoa ERUPTS. About 172 dB, measured 160 KM away!", n_at=43.2),
    dict(id="wave", s=49.5, e=TW, bg="space", clock="5 DAYS", char="earth", pos=(560, 1060, 480),
         props=with_meter(wave_props), look=(0, 0),
         narr="People 4,800 KM away heard it. Its pressure wave circled EARTH about 7 TIMES.", n_at=49.7),
    dict(id="twist", s=TW, e=63.0, bg="twist", clock="WAIT...", char="kid", state="puff", pos=(540, 1080, 380),
         props=with_meter(twist_props), twist=True, look=(0, -0.2),
         narr="Twist: Earth's air CAN'T get louder than about 194 dB. Push past it: SHOCKWAVE.", n_at=TW + 0.2,
         say="Volume MAXED out!", say_at=TW + 3.4, pitch=620),
    dict(id="safety", s=63.0, e=69.0, bg="diwali", clock="THIS DIWALI", char="diya", pos=(540, 1080, 400),
         props=safety_props, look=(0, -0.2),
         narr="Noise damage is PERMANENT. Enjoy Diwali from a SAFE distance.", n_at=63.2,
         say="Ears FIRST!", say_at=65.8, pitch=520),
    dict(id="outro", s=69.0, e=74.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_out(clamp((T - 1.9) / 0.5))
        for k in range(5):
            h = (60 + 70 * k) * p * (0.8 + 0.2 * math.sin(T * 8 + k))
            x = 340 + k * 100
            d.rounded_rectangle([x - 34, 1560 - h, x + 34, 1560], 12,
                                fill=[(90, 210, 110), (160, 220, 90), (255, 210, 60), (255, 140, 60), (240, 70, 60)][k],
                                outline=OUTL, width=5)

cfg = dict(
    total=74.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("your ", WHITE), ("VOICE", YEL)], 130), 770, 0.75, "right"),
        (title([("kept getting", WHITE)], 110), 905, 1.05, "left"),
        (title([("LOUDER?", YEL)], 170), 1070, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Loudest thing ", WHITE), ("YOU", YEL)], 92), 470, 0.15),
                      (title([("have ever heard?", WHITE)], 92), 600, 0.45)],
               row=[("kid", 1), ("cat", 1), ("auto", 1), ("diya", 1), ("earth", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, g=0.9),
           dict(t0=69.0, t1=74.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.06)],
    fx=[("whistle", 24.0, 0.5), ("whistle", 25.5, 0.5), ("boom", 31.4, 0.6), ("boom", 33.4, 0.6),
        ("rumble", 36.8, 0.6, dict(dd=5.0)), ("boom", 43.6, 1.0), ("rumble", 43.8, 0.7, dict(dd=5.0)),
        ("wind", 49.7, 0.4, dict(dd=6.0)), ("boom", TW + 1.0, 0.7)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_louder")
