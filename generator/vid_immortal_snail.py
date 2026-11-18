#!/usr/bin/env python3
"""What if an immortal snail chased you? Based on the 'immortal snail' internet thought experiment. Facts: garden
snails (Cornu aspersum) crawl ~4.5 cm per 30 s on a smooth surface, about 1.5 mm/s (Pembury Smith & Ruxton 2021,
J Zool, St Andrews); we use a conservative ~1 mm/s = 3.6 m/h = 86.4 m/day. Snails glide on a thin layer of mucus
pushed by waves of muscle contraction along the foot ('pedal waves'; Denny 1980, Science). Great-circle distances
computed with the haversine formula: Delhi-Mumbai ~1,150 km -> ~36 years at 86.4 m/day; Delhi-London ~6,700 km ->
~213 years; Earth's equator 40,075 km -> ~1,270 years. 1 km -> ~11.6 days. Tracked UK garden snails reached a top
speed of ~1 m an hour and covered up to ~25 m in 24 hours (Univ. of Exeter, Dave Hodgson, 2013). Twist: limpets
(small aquatic snails) have goethite-fibre teeth that are the strongest biological material yet tested,
potentially stronger than spider silk (Barber et al., J R Soc Interface 2015, Univ. of Portsmouth)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from vid_salt_slug import slug, slime_trail, garden_bg, _PS, _PH

TW = 67.0
SHELL = (196, 120, 60)
SHELL_D = (150, 84, 40)
SBODY = (200, 176, 150)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def put(frame, txt, cx, y, size=52, col=WHITE):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2)):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, 0, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- snail
def snail(frame, cx, cy, L, T, wig=1.0, sleep=False, glow=False):
    hx, hy, Hh, L2 = slug(frame, cx, cy, L, T, eyes=0.25 if sleep else 1.0, wig=wig, col=SBODY)
    d = ImageDraw.Draw(frame)
    sx, sy = cx - L * 0.06, cy - Hh * 1.45
    R = L * 0.27
    if glow:
        for k in range(3):
            g = R + 30 + k * 18 + 6 * math.sin(T * 4)
            d.ellipse([sx - g, sy - g, sx + g, sy + g], outline=(180, 120, 255), width=6)
    d.ellipse([sx - R, sy - R, sx + R, sy + R], fill=SHELL, outline=OUTL, width=max(4, int(L / 90)))
    pts = []
    for k in range(120):
        a = k / 119 * 4.2 * math.pi
        r = R * 0.9 * (1 - k / 125)
        pts.append((sx + r * math.cos(a + T * 0.2 * 0), sy + r * math.sin(a)))
    d.line(pts[::-1], fill=SHELL_D, width=max(4, int(L / 70)), joint="curve")
    if sleep:
        for k in range(3):
            ph = (T * 0.5 + k / 3) % 1
            put(frame, "z", hx + 40 + 50 * ph + 20 * k, hy - 120 - 160 * ph, 44 + 14 * k, WHITE)
    return hx, hy

def bag(d, x, y, s):
    d.ellipse([x - 70 * s, y - 60 * s, x + 70 * s, y + 80 * s], fill=(200, 160, 90), outline=OUTL, width=6)
    d.polygon([(x - 30 * s, y - 60 * s), (x + 30 * s, y - 60 * s), (x + 45 * s, y - 100 * s), (x - 45 * s, y - 100 * s)],
              fill=(200, 160, 90), outline=OUTL)
    d.line([(x - 34 * s, y - 64 * s), (x + 34 * s, y - 64 * s)], fill=(140, 60, 40), width=8)

def plane(d, x, y, s, ang):
    c, sn = math.cos(ang), math.sin(ang)
    m = -1 if c < 0 else 1
    P = lambda px, py: (x + (px * c - m * py * sn) * s, y + (px * sn + m * py * c) * s)
    d.polygon([P(-90, -14), P(80, -14), P(110, 0), P(80, 14), P(-90, 14)], fill=WHITE, outline=OUTL)
    d.polygon([P(-10, 0), P(30, 0), P(-20, 80), P(-40, 80)], fill=(220, 230, 240), outline=OUTL)
    d.polygon([P(-10, 0), P(30, 0), P(-20, -80), P(-40, -80)], fill=(220, 230, 240), outline=OUTL)
    d.polygon([P(-90, 0), P(-70, 0), P(-90, -50), P(-100, -50)], fill=(230, 60, 60), outline=OUTL)

_bg = {}
def flat_bg(key, top, bot):
    if key not in _bg:
        y = np.linspace(0, 1, H)[:, None]
        a = (np.array(top) * (1 - y[..., None]) + np.array(bot) * y[..., None]).astype(np.uint8)
        _bg[key] = Image.fromarray(np.broadcast_to(a, (H, W, 3)).copy()).convert("RGBA")
    return _bg[key]

def map_bg(T): return flat_bg("map", (120, 190, 140), (90, 160, 120))
def sky_bg(T): return flat_bg("sky", (80, 150, 235), (200, 230, 250))
def lab_bg(T): return flat_bg("lab", (230, 236, 246), (200, 212, 230))
def rock_bg(T): return flat_bg("rock", (80, 170, 220), (40, 110, 180))

# ---------------------------------------------------------------- props
def deal_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k, (x, y) in enumerate(((720, 1130), (880, 1150), (800, 1010))):
        if lt > 0.3 + k * 0.25:
            q = ease_back(clamp((lt - 0.3 - k * 0.25) / 0.4))
            bag(d, x, y, 0.9 * q + 0.01)
    if lt > 1.2: put(frame, "100 CRORE", 800, 1230, 64, YEL)
    if lt > 2.0: top_label(frame, "+ NEVER AGE", 380, YEL, 96)

def rule_props(frame, d, T, sc):
    lt = T - sc["s"]
    x = 400 + 8 * lt
    slime_trail(d, 20, x - 200, 1186, T)
    snail(frame, x, 1186, 520, T, glow=True)
    if lt > 0.4: top_label(frame, "1 TOUCH = GAME OVER", 380, YEL, 84)

def speed_props(frame, d, T, sc):
    lt = T - sc["s"]
    # ruler
    d.rectangle([90, 1190, 990, 1280], fill=(250, 220, 90), outline=OUTL, width=5)
    for k in range(46):
        x = 110 + k * 19
        h = 40 if k % 10 == 0 else (26 if k % 5 == 0 else 16)
        d.line([(x, 1190), (x, 1190 + h)], fill=OUTL, width=3)
    snail(frame, 470 + 8 * lt, 1186, 560, T)
    secs = int(clamp(lt / 6.5) * 60)
    put(frame, f"{secs} SEC", 540, 700, 80, WHITE)
    if lt > 0.4: top_label(frame, "~1 MM A SECOND", 380, YEL, 96)
    if lt > 3.4: put(frame, "= ~3.6 M AN HOUR", 540, 540, 64, YEL)

def foot_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([0, 1186, W, 1300], fill=(140, 210, 240))
    put(frame, "SLIME FILM", 540, 1210, 52, WHITE)
    snail(frame, 520, 1186, 860, T, wig=0.4)
    # pedal waves: dark bands sliding along the foot
    L = 860
    for k in range(7):
        ph = ((T * 0.5 + k / 7) % 1)
        x = 520 - L * 0.45 + ph * L * 0.9
        d.rectangle([x - 12, 1170, x + 12, 1184], fill=(120, 96, 80))
    if lt > 0.4: top_label(frame, "MUSCLE WAVES", 380, YEL, 100)

def km_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = clamp((lt - 0.4) / 5.8)
    d.rectangle([80, 1190, 1000, 1210], fill=(240, 240, 240), outline=OUTL, width=3)
    put(frame, "0", 90, 1230, 48, WHITE); put(frame, "1 KM", 960, 1230, 48, WHITE)
    snail(frame, 160 + g * 760, 1186, 200, T)
    day = 1 + int(g * 11.6)
    put(frame, f"DAY {min(day, 12)}", 540, 700, 96, YEL)
    if lt > 0.4: top_label(frame, "~86 M A DAY", 380, YEL, 100)

def path_pt(p1, p2, t, bulge):
    return (p1[0] + (p2[0] - p1[0]) * t + bulge * math.sin(t * math.pi), p1[1] + (p2[1] - p1[1]) * t)

def map_props(frame, d, T, sc):
    lt = T - sc["s"]
    p1, p2 = (330, 640), (300, 1240)
    for k in range(18):
        x, y = path_pt(p1, p2, k / 17, -120)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=WHITE)
    for (x, y), name in ((p1, "DELHI"), (p2, "MUMBAI")):
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=(230, 60, 60), outline=OUTL, width=6)
        put(frame, name, x + 210, y - 30, 60, WHITE)
    g = clamp((lt - 0.3) / 5.8)
    x, y = path_pt(p1, p2, g, -120)
    snail(frame, x, y + 20, 150, T)
    put(frame, f"YEAR {1 + int(g * 35.4)}", 760, 940, 84, YEL)
    if lt > 0.4: top_label(frame, "~1,150 KM", 380, YEL, 100)

def flight_props(frame, d, T, sc):
    lt = T - sc["s"]
    p1, p2 = (880, 1180), (200, 760)
    for k in range(20):
        t = k / 19
        x = p1[0] + (p2[0] - p1[0]) * t; y = p1[1] + (p2[1] - p1[1]) * t - 260 * math.sin(t * math.pi)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=WHITE)
    for (x, y), name in ((p1, "DELHI"), (p2, "LONDON")):
        d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=(230, 60, 60), outline=OUTL, width=6)
        put(frame, name, x, y + 40, 56, WHITE)
    g = ease_out(clamp((lt - 0.3) / 3.5))
    x = p1[0] + (p2[0] - p1[0]) * g; y = p1[1] + (p2[1] - p1[1]) * g - 260 * math.sin(g * math.pi)
    ta, tb = min(g, 0.98), min(g, 0.98) + 0.02
    xa = p1[0] + (p2[0] - p1[0]) * ta; ya = p1[1] + (p2[1] - p1[1]) * ta - 260 * math.sin(ta * math.pi)
    xb = p1[0] + (p2[0] - p1[0]) * tb; yb = p1[1] + (p2[1] - p1[1]) * tb - 260 * math.sin(tb * math.pi)
    ang = math.atan2(yb - ya, xb - xa)
    plane(d, x, y, 0.8, ang)
    snail(frame, 600, 1370, 150, T)
    if lt > 0.4: top_label(frame, "~6,700 KM", 380, YEL, 100)
    if lt > 3.8: put(frame, "200+ YEARS AHEAD", 540, 540, 68, YEL)

def earth_props(frame, d, T, sc):
    lt = T - sc["s"]
    a = -math.pi / 2 + clamp(lt / 6.2) * 2 * math.pi
    r = 250
    x, y = 540 + r * math.cos(a), 1020 + r * math.sin(a)
    snail(frame, x, y + 20, 110, T)
    if lt > 0.4: top_label(frame, "~40,000 KM", 380, YEL, 100)
    if lt > 2.5: put(frame, "~1,270 YEARS", 540, 560, 72, YEL)

def real_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a leaf blanket
    snail(frame, 540, 1186, 560, T, wig=0.0, sleep=True)
    if lt > 0.4: top_label(frame, "NAP TIME", 380, YEL, 110)
    if lt > 2.0: put(frame, "MAX ~25 M A DAY", 540, 540, 68, WHITE)

def limpet(d, cx, cy, s, T):
    d.chord([cx - 170 * s, cy - 170 * s, cx + 170 * s, cy + 170 * s], 180, 360, fill=(200, 180, 150), outline=OUTL,
            width=6)
    for k in range(-4, 5):
        d.line([(cx, cy - 160 * s), (cx + k * 38 * s, cy)], fill=(160, 140, 110), width=4)
    d.ellipse([cx - 22 * s, cy - 180 * s, cx + 22 * s, cy - 140 * s], fill=(230, 214, 190), outline=OUTL, width=4)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.polygon([(0, 1300), (120, 1150), (420, 1120), (760, 1150), (1080, 1100), (1080, H), (0, H)],
              fill=(110, 110, 120), outline=OUTL)
    p = ease_back(clamp(lt / 0.6))
    limpet(d, 520, 1140, p + 0.01, T)
    if lt > 2.0:
        # magnified tooth in a circle
        cx, cy, r = 800, 760, 150
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 246, 255), outline=YEL, width=10)
        d.polygon([(cx - 50, cy - 70), (cx + 40, cy - 80), (cx + 70, cy + 70), (cx + 20, cy + 40), (cx - 10, cy + 90)],
                  fill=(150, 90, 50), outline=OUTL)
        d.line([(640, 1000), (cx - r * 0.6, cy + r * 0.8)], fill=YEL, width=8)
    if lt > 0.4: top_label(frame, "LIMPET TEETH", 380, YEL, 104)
    if lt > 3.4: put(frame, "TOUGHER THAN SPIDER SILK?", 540, 520, 56, WHITE)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="deal", s=4.0, e=11.0, bg_fn=lambda T: garden_bg(), clock="THE DEAL", props=deal_props, char="kid",
         pos=(300, 1100, 360), look=(0.6, 0.0),
         narr="The deal: 100 CRORE rupees and you NEVER age. The catch? An IMMORTAL snail.", n_at=4.2,
         narr_y=1580, say="EASY money!", say_at=7.8, pitch=440),
    dict(id="rule", s=11.0, e=18.0, bg_fn=lambda T: garden_bg(), clock="THE RULE", props=rule_props, char="kid",
         pos=(870, 1080, 280), look=(-0.6, 0.1),
         narr="It always knows where you are and NEVER stops. If it touches you, GAME OVER.", n_at=11.2,
         narr_y=1580),
    dict(id="speed", s=18.0, e=25.0, bg_fn=lab_bg, clock="GOOD NEWS", props=speed_props,
         narr="Good news: a garden snail crawls about 1 MM a second. That's under 4 METRES an hour.",
         n_at=18.2, narr_y=1580),
    dict(id="foot", s=25.0, e=32.0, bg_fn=lab_bg, clock="HOW?", props=foot_props,
         narr="It glides on a thin film of SLIME, pushed by ripples of muscle along its FOOT.", n_at=25.2,
         narr_y=1580),
    dict(id="km", s=32.0, e=39.0, bg="living", clock="1 KM", props=km_props, char="kid",
         pos=(220, 900, 240), look=(0.6, 0.6),
         narr="Crawling nonstop, it covers about 86 M a day. One KM takes it about 12 DAYS.", n_at=32.2,
         narr_y=1580),
    dict(id="map", s=39.0, e=46.0, bg_fn=map_bg, clock="ROAD TRIP", props=map_props,
         narr="Delhi to MUMBAI is about 1,150 km as the crow flies. That's 36 YEARS of crawling.",
         n_at=39.2, narr_y=1580),
    dict(id="flight", s=46.0, e=53.0, bg_fn=sky_bg, clock="ESCAPE", props=flight_props,
         narr="One flight to LONDON, about 6,700 km, buys you over 200 YEARS of head start.", n_at=46.2,
         narr_y=1580),
    dict(id="earth", s=53.0, e=60.0, bg="space", clock="FULL LAP", props=earth_props, char="earth",
         pos=(540, 1020, 520),
         narr="Crawling all the way around EARTH, about 40,000 km, takes it some 1,270 YEARS.", n_at=53.2,
         narr_y=1580),
    dict(id="real", s=60.0, e=TW, bg_fn=lambda T: garden_bg(), clock="REAL LIFE", props=real_props,
         narr="Real garden snails REST a lot. Tracked UK snails covered at most about 25 M a day.", n_at=60.2,
         narr_y=1580),
    dict(id="twist", s=TW, e=74.0, bg_fn=rock_bg, clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: its sea cousin the LIMPET has TEETH that may be the strongest natural material known!",
         n_at=TW + 0.2, narr_y=1580),
    dict(id="outro", s=74.0, e=79.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        snail(frame, 540, 1540, 420 * p + 2, T, glow=p > 0.9)

cfg = dict(
    total=79.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 470, 0.2, "pop"),
        (title([("AN IMMORTAL SNAIL", WHITE)], 110), 680, 0.75, "right"),
        (title([("CHASED YOU?", YEL)], 150), 810, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" take", WHITE)], 100), 470, 0.15),
                      (title([("the deal?", YEL)], 104), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("earth", 1), ("worm", 1), ("samosa", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, melody=True),
           dict(t0=11.0, t1=18.0, minor=True), dict(t0=18.0, t1=53.0, melody=True),
           dict(t0=53.0, t1=60.0, melody=True, drums=False), dict(t0=60.0, t1=TW - 0.15, drums=False),
           dict(t0=TW + 2.0, t1=79.0, melody=True)],
    drones=[dict(t0=11.0, dur=7.0, g=0.10), dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("ding", 5.4, 0.2), ("heartbeat", 11.5, 0.2, dict(dd=6.0)), ("tick", 19.0, 0.2), ("tick", 20.0, 0.2),
        ("whoosh", 46.5, 0.3, dict(dd=1.2)), ("ding", 50.4, 0.2), ("ding", 56.0, 0.2),
        ("waves", TW + 0.5, 0.2, dict(dd=6.0)), ("ding", TW + 2.2, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_an_immortal_snail_chased_you")
