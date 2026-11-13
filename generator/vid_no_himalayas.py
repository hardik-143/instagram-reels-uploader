#!/usr/bin/env python3
"""What if India had no Himalayas? Facts: the Himalayas run roughly 2,400 km (Britannica; USGS gives ~2,900 km
for the wider system) and include Everest, 8,848.86 m. They block cold, dry winter winds from Central Asia/Siberia
from reaching north India (NCERT climate chapter; PMF IAS). Boos & Kuang (Nature 2010, Harvard SEAS summary): the
narrow Himalayan barrier powers the South Asian monsoon by insulating warm, moist air over India from cold, dry
extratropical air; in their model the monsoon survives removing the Tibetan Plateau as long as the mountain wall
stays. Himalayan glaciers feed the Ganga, Yamuna and Brahmaputra, and Himalayan river sediment built the alluvial
Indo-Gangetic plain (NCERT; PMF IAS). India met Asia about 40-50 million years ago and still moves north at about
half its earlier ~9 m per century, i.e. ~4-5 cm a year (USGS 'The Himalayas: Two continents collide'), similar to
how fast fingernails grow. Twist: Everest's summit is Qomolangma Limestone, ~470 million years old, laid down on
a seafloor and holding fragments of marine shells such as trilobites and brachiopods (Montana State University)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
GROUND = 1330

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2)):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, 0, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def sky(top=(90, 160, 240), bot=(214, 236, 252)):
    y = np.linspace(0, 1, H)[:, None]
    a = (np.array(top) * (1 - y[..., None]) + np.array(bot) * y[..., None]).astype(np.uint8)
    return Image.fromarray(np.broadcast_to(a, (H, W, 3)).copy()).convert("RGBA")

def mountain(d, cx, base, h, w, col=(120, 110, 130), snow=0.32):
    if h < 4: return
    peak = (cx, base - h)
    d.polygon([(cx - w, base), peak, (cx + w, base)], fill=col, outline=OUTL)
    sx = w * snow; sy = h * snow
    d.polygon([(cx - sx, base - h + sy), peak, (cx + sx, base - h + sy), (cx + sx * 0.4, base - h + sy * 0.8),
               (cx, base - h + sy * 1.1), (cx - sx * 0.4, base - h + sy * 0.8)], fill=(250, 252, 255), outline=OUTL)

RANGE = [(-40, 300, 230), (180, 380, 240), (420, 460, 250), (660, 560, 260), (900, 430, 250), (1110, 340, 230)]

def draw_range(d, k=1.0, base=GROUND):
    for cx, h, w in RANGE:
        mountain(d, cx, base, h * k, w, (128, 116, 140) if cx != 660 else (112, 100, 128))

def plain_bg(key, top=(90, 160, 240), bot=(214, 236, 252), ground=(120, 170, 90), clouds=True):
    if key not in _cache:
        img = sky(top, bot); d = ImageDraw.Draw(img)
        if clouds:
            for cx, cy, s in ((200, 560, 0.9), (860, 700, 0.7)):
                for dx, r in ((-60, 50), (0, 70), (60, 50)):
                    d.ellipse([cx + (dx - r) * s, cy - r * s, cx + (dx + r) * s, cy + r * s], fill=WHITE)
        d.rectangle([0, GROUND, W, H], fill=ground)
        _cache[key] = img
    return _cache[key]

def green_bg(T): return plain_bg("green")
def cold_bg(T): return plain_bg("cold", (120, 150, 190), (220, 230, 240), (200, 215, 225), False)
def dry_bg(T): return plain_bg("dry", (150, 190, 230), (240, 230, 200), (200, 170, 110), False)

# ---------------------------------------------------------------- props
def wall_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp(lt / 1.2))
    draw_range(d, p)
    if lt > 1.2:
        d.line([(660, GROUND - 560), (660, GROUND - 680)], fill=OUTL, width=8)
        d.polygon([(660, GROUND - 680), (740, GROUND - 658), (660, GROUND - 636)], fill=(230, 50, 60), outline=OUTL)
        lab_at(frame, "EVEREST 8,849 M", 640, GROUND - 730, YEL, 52)
    if lt > 2.4: top_label(frame, "OVER 2,000 KM LONG", 400, WHITE, 66)

def vanish_props(frame, d, T, sc):
    lt = T - sc["s"]
    k = 1 - ease_out(clamp((lt - 0.8) / 1.6))
    draw_range(d, k)
    if lt > 2.4:
        q = ease_back(clamp((lt - 2.4) / 0.4))
        top_label(frame, "POOF!", 420, YEL, int(60 + 50 * q))

def cold_props(frame, d, T, sc):
    lt = T - sc["s"]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for k in range(9):
        y = 560 + 70 * k
        x = (W + 300) - ((lt * 520 + k * 170) % (W + 600))
        ld.line([(x, y), (x + 260, y)], fill=(255, 255, 255, 200), width=8)
        ld.arc([x - 50, y - 60, x + 30, y], 90, 270, fill=(255, 255, 255, 200), width=8)
    rng = np.random.default_rng(5)
    for k in range(40):
        x0 = rng.uniform(0, W + 400); y0 = rng.uniform(0, 1300)
        x = (x0 - lt * 300) % (W + 100); y = (y0 + lt * 120) % 1300 + 300
        ld.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 255, 255, 230))
    frame.alpha_composite(lay)
    lab_at(frame, "FROM CENTRAL ASIA", 760, 470, WHITE, 52)

def monsoon_props(frame, d, T, sc):
    lt = T - sc["s"]
    # rain clouds drift north (left to right) and keep going: nothing stops them
    for k in range(3):
        x = -200 + ((lt * 210 + k * 400) % 1500)
        y = 620 + 60 * k
        mini(frame, "cloud", x, y, 230, T)
    if lt > 1.0:
        lab_at(frame, "SOUTH", 120, 1250, WHITE, 44)
        lab_at(frame, "NORTH", 960, 1250, WHITE, 44)
    if lt > 3.4: top_label(frame, "WEAKER MONSOON", 400, YEL, 72)

def river_props(frame, d, T, sc):
    lt = T - sc["s"]
    mountain(d, 830, GROUND, 520, 320, (120, 110, 135), 0.45)
    dry = ease_out(clamp((lt - 3.2) / 1.5))
    w = int(46 * (1 - dry)) + 2
    col = (60, 140, 220) if dry < 0.95 else (170, 140, 90)
    pts = [(830, GROUND - 330), (720, GROUND - 180), (760, GROUND - 60), (560, GROUND + 60), (300, GROUND + 140),
           (40, GROUND + 230)]
    d.line(pts, fill=col, width=w, joint="curve")
    lab_at(frame, "GLACIER", 830, GROUND - 600, WHITE, 48)
    if lt > 1.2: top_label(frame, "GANGA  YAMUNA  BRAHMAPUTRA", 400, YEL, 52)

def plain_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.3) / 2.0))
    d.rectangle([0, 1040, W, GROUND], fill=(130, 180, 80))
    for row in range(4):
        y = 1060 + row * 64
        for k in range(int(12 * p)):
            x = 50 + k * 88 + (row % 2) * 40
            d.line([(x, y + 40), (x, y)], fill=(90, 140, 50), width=6)
            d.ellipse([x - 9, y - 22, x + 9, y + 6], fill=(230, 190, 70), outline=OUTL, width=2)
    if lt > 1.8: top_label(frame, "INDO-GANGETIC PLAIN", 400, YEL, 66)

def rise_props(frame, d, T, sc):
    lt = T - sc["s"]
    k = ease_out(clamp((lt - 0.3) / 1.4))
    draw_range(d, k)
    if lt > 2.0:
        y = 520
        d.line([(160, y), (520, y)], fill=YEL, width=14)
        d.polygon([(520, y - 30), (580, y), (520, y + 30)], fill=YEL, outline=OUTL)
        lab_at(frame, "INDIA", 300, y - 60, WHITE, 52)
        lab_at(frame, "4-5 CM A YEAR", 760, y, YEL, 54)

def fossil(d, x, y, s, col=(230, 220, 200)):
    d.ellipse([x - s, y - s * 0.75, x + s, y + s * 0.75], fill=col, outline=OUTL, width=4)
    for k in range(1, 4):
        r = s * (1 - k * 0.22)
        d.arc([x - r, y - r * 0.75, x + r, y + r * 0.75], 200, 520, fill=OUTL, width=3)
    for k in range(-3, 4):
        d.line([(x + k * s * 0.22, y - s * 0.7), (x + k * s * 0.22, y + s * 0.7)], fill=(150, 140, 120), width=2)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    mountain(d, 540, GROUND, 760, 460, (112, 100, 128), 0.25)
    if lt > 0.8:
        for k, (x, y, s) in enumerate(((470, 820, 40), (600, 900, 46), (520, 1020, 52), (640, 1100, 44))):
            if lt > 0.8 + k * 0.4:
                q = ease_back(clamp((lt - 0.8 - k * 0.4) / 0.4))
                fossil(d, x, y, s * q + 1)
    if lt > 2.6: top_label(frame, "~470 MILLION YEARS OLD", 400, YEL, 62)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wall", s=4.0, e=11.0, bg_fn=green_bg, clock="NORTH INDIA", props=wall_props,
         narr="The Himalayas: a wall of mountains over 2,000 KM long, topped by EVEREST.", n_at=4.2,
         narr_y=1560),
    dict(id="vanish", s=11.0, e=18.0, bg_fn=green_bg, clock="OVERNIGHT", props=vanish_props, char="uncle",
         state="hat", pos=(540, 1180, 260), look=(0, -0.3),
         narr="Now imagine they VANISHED overnight. North India is suddenly wide OPEN.", n_at=11.2,
         narr_y=1560, say="PAHAD kahan gaye?", say_at=14.6, pitch=150, bubble_y=760),
    dict(id="cold", s=18.0, e=25.0, bg_fn=cold_bg, clock="WINTER", props=cold_props, char="uncle",
         pos=(320, 1120, 300), look=(0.5, 0),
         narr="The wall blocks freezing winter winds from CENTRAL ASIA. Now they'd blow straight in.",
         n_at=18.2, narr_y=1560, say="Itni THAND!", say_at=21.6, pitch=150, bubble_y=760),
    dict(id="monsoon", s=25.0, e=32.0, bg_fn=green_bg, clock="MONSOON", props=monsoon_props,
         narr="It also traps warm, wet MONSOON air. A climate model says the wall is KEY to the rains.",
         n_at=25.2, narr_y=1560),
    dict(id="rivers", s=32.0, e=39.0, bg_fn=dry_bg, clock="RIVERS", props=river_props,
         narr="Himalayan GLACIERS feed the Ganga, Yamuna and Brahmaputra. No peaks, no SNOWMELT.",
         n_at=32.2, narr_y=1600),
    dict(id="plain", s=39.0, e=46.0, bg_fn=green_bg, clock="FARMS", props=plain_props, char="kid",
         pos=(540, 800, 260), look=(0, 0.4),
         narr="Their rivers carried mountain soil that BUILT the fertile Indo-Gangetic plain.", n_at=39.2,
         narr_y=1560),
    dict(id="rise", s=46.0, e=TW, bg_fn=green_bg, clock="GOOD NEWS", props=rise_props,
         narr="Relax, they're real, and growing: India still pushes NORTH about as fast as nails grow.",
         n_at=46.2, narr_y=1560),
    dict(id="twist", s=TW, e=60.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: Everest's summit rock formed on an ancient SEAFLOOR. It holds fossil SEA SHELLS!",
         n_at=TW + 0.2, narr_y=1560),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.1)
        mountain(d, 540, 1560, 280 * p + 1, 240, (120, 110, 135))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("INDIA HAD NO", WHITE)], 130), 690, 0.75, "right"),
        (title([("HIMALAYAS?", YEL)], 160), 830, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL), (" miss", WHITE)], 96), 470, 0.15),
                      (title([("the most?", YEL)], 104), 600, 0.45)],
               row=[("kid", 1), ("uncle", "hat"), ("cloud", 1), ("earth", 1), ("chai", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0, minor=True), dict(t0=32.0, t1=39.0, minor=True, drums=False),
           dict(t0=39.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("rumble", 4.4, 0.2, dict(dd=1.5)), ("powerdown", 12.0, 0.25), ("pop", 13.5, 0.3),
        ("gale", 18.3, 0.25, dict(dd=6.0)), ("wind", 25.3, 0.2, dict(dd=6.0)), ("ding", 29.0, 0.2),
        ("rumble", 46.4, 0.2, dict(dd=1.5)), ("ding", 48.4, 0.2), ("pop", TW + 1.0, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_india_had_no_himalayas")
