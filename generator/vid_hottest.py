#!/usr/bin/env python3
"""What if you chased the hottest temperature ever? A temperature ladder: Phalodi 51 °C, India's record (19 May 2016,
CNN/WWA); chai boils at 100 °C; basaltic lava up to ~1,200 °C (Universe Today); Sun's surface ~5,500 °C (NASA);
lightning ~30,000 °C, 5x the Sun's surface (BBC Science Focus); Sun's core ~15 million °C and ITER's plasma
150 million °C+, 10x the Sun's core (iter.org; India is an ITER member); LHC/ALICE lead-ion collisions, 2012,
over 5 trillion degrees (Guinness World Records).
Twist: the LHC's magnets run at 1.9 K (-271.3 °C), colder than outer space's 2.7 K (-270.5 °C) (CERN)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 56.0   # twist starts

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

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

# ---------------------------------------------------------------- thermometer on the left edge, level rises scene by scene
LEVELS = {"phalodi": 0.12, "chai": 0.22, "lava": 0.34, "sunskin": 0.46, "bolt": 0.57, "core": 0.68, "fusion": 0.8,
          "lhc": 1.0}
_prev = {"phalodi": 0.0, "chai": 0.12, "lava": 0.22, "sunskin": 0.34, "bolt": 0.46, "core": 0.57, "fusion": 0.68,
         "lhc": 0.8}

def thermo(frame, d, T, sc):
    lt = T - sc["s"]
    lv = _prev[sc["id"]] + (LEVELS[sc["id"]] - _prev[sc["id"]]) * ease_out(clamp(lt / 1.2))
    x, top, bot = 80, 480, 1200
    d.rounded_rectangle([x - 26, top, x + 26, bot], 26, fill=(250, 250, 255), outline=OUTL, width=5)
    d.ellipse([x - 48, bot - 30, x + 48, bot + 66], fill=(230, 50, 50), outline=OUTL, width=5)
    yl = bot - (bot - top - 20) * lv
    d.rounded_rectangle([x - 14, yl, x + 14, bot + 10], 14, fill=(230, 50, 50))
    for k in range(1, 8):
        yy = bot - (bot - top) * k / 8
        d.line([(x + 26, yy), (x + 44, yy)], fill=OUTL, width=4)

def with_thermo(fn=None):
    def p(frame, d, T, sc):
        if fn: fn(frame, d, T, sc)
        thermo(frame, d, T, sc)
    return p

# ---------------------------------------------------------------- scene props
def sweat(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(4):
        ph = (lt * 0.8 + k / 4) % 1.0
        x = 540 + (k - 1.5) * 150; y = 860 + ph * 140
        d.ellipse([x - 12, y - 18, x + 12, y + 18], fill=(150, 210, 255), outline=OUTL, width=3)
    for k in range(3):     # heat shimmer lines
        y = 520 + k * 50
        pts = [(260 + i * 40, y + 10 * math.sin(lt * 6 + i + k)) for i in range(15)]
        d.line(pts, fill=(255, 240, 200), width=5)

def steam(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(5):
        ph = (lt * 0.6 + k / 5) % 1.0
        x = 540 + (k - 2) * 60 + 20 * math.sin(lt * 3 + k); y = 840 - ph * 200
        r = 18 + 30 * ph
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255), width=6)

def lava_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.polygon([(180, 1320), (420, 760), (660, 760), (900, 1320)], fill=(90, 60, 50), outline=OUTL)
    glow(frame, 540, 760, 220, (255, 120, 40), 0.9)
    d.polygon([(420, 760), (660, 760), (600, 900), (560, 1320), (500, 1320), (470, 900)], fill=(255, 110, 30))
    for k in range(6):
        ph = (lt * 0.9 + k / 6) % 1.0
        x = 540 + (k - 2.5) * 50; y = 740 - ph * 180
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(255, 190, 60), outline=OUTL, width=3)

def sun_glow(frame, d, T, sc):
    glow(frame, 540, 1060, 470, (255, 200, 80), 0.7)

def bolt_props(frame, d, T, sc):
    lt = T - sc["s"]
    on = (lt % 1.3) < 0.18
    pts = [(560, 980), (500, 1100), (580, 1120), (480, 1310), (620, 1080), (540, 1070), (600, 980)]
    if on:
        glow(frame, 540, 1140, 300, (230, 230, 255), 0.8)
    d.polygon(pts, fill=(255, 240, 120) if on else (255, 220, 60), outline=OUTL)

def core_props(frame, d, T, sc):
    glow(frame, 540, 1060, 480, (255, 180, 60), 0.75)
    glow(frame, 540, 1060, 140, (255, 255, 230), 1.0)

def tokamak(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1080
    d.ellipse([cx - 360, cy - 170, cx + 360, cy + 170], fill=(150, 160, 190), outline=OUTL, width=6)
    d.ellipse([cx - 170, cy - 70, cx + 170, cy + 70], fill=(40, 40, 70), outline=OUTL, width=6)
    # glowing plasma ring
    for k in range(3):
        r1, r2 = 270 - k * 8, 120 - k * 4
        a = 0.6 + 0.4 * math.sin(lt * 8 + k)
        c = (255, int(120 + 100 * a), 255)
        d.ellipse([cx - r1, cy - r2, cx + r1, cy + r2], outline=c, width=10)

def ring_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, rx, ry = 540, 1060, 400, 190
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(120, 140, 200), width=40)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=OUTL, width=4)
    for s in (1, -1):
        a = lt * 4 * s
        x = cx + rx * math.cos(a); y = cy + ry * math.sin(a)
        glow(frame, x, y, 60, (255, 230, 150), 0.9)
    if lt > 2.2:
        q = ease_out(clamp((lt - 2.2) / 0.4))
        glow(frame, cx + rx, cy, 60 + 200 * q, (255, 255, 220), 0.9)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, rx, ry = 540, 1060, 430, 200
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(170, 220, 255), width=40)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=OUTL, width=4)
    for k in range(10):   # frost flakes
        a = k * 0.63 + lt * 0.3
        x = cx + rx * math.cos(a); y = cy + ry * math.sin(a)
        for ang in (0, 60, 120):
            r = math.radians(ang)
            d.line([(x - 18 * math.cos(r), y - 18 * math.sin(r)), (x + 18 * math.cos(r), y + 18 * math.sin(r))],
                   fill=WHITE, width=5)
    if lt > 2.8:
        top_label(frame, "MAGNETS: -271.3 °C", 360, (150, 220, 255), 64)
        top_label(frame, "SPACE: -270.5 °C", 450, WHITE, 52)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="phalodi", s=4.0, e=10.5, bg="hot", clock="51 °C", char="kid", pos=(560, 1060, 480),
         props=with_thermo(sweat), look=(0, -0.3),
         narr="Start with India's hottest day ever: 51 °C in PHALODI, Rajasthan, 2016.", n_at=4.2,
         say="Thoda AC chalao!", say_at=7.0, pitch=620),
    dict(id="chai", s=10.5, e=17.0, bg="day", clock="100 °C", char="chai", pos=(560, 1060, 440),
         props=with_thermo(steam), look=(0, -0.3),
         narr="Hotter. At 100 °C, water BOILS. Perfect for chai.", n_at=10.7,
         say="Now we're TALKING!", say_at=13.3, pitch=480),
    dict(id="lava", s=17.0, e=23.5, bg="night", clock="1,200 °C", props=with_thermo(lava_props),
         narr="Basalt LAVA erupts at up to about 1,200 °C. Rock turns LIQUID.", n_at=17.2),
    dict(id="sunskin", s=23.5, e=30.0, bg="space", clock="5,500 °C", char="sun", pos=(560, 1060, 520),
         props=with_thermo(sun_glow), look=(0, 0),
         narr="The Sun's SURFACE: about 5,500 °C.", n_at=23.7,
         say="Feeling WARM yet?", say_at=26.0, pitch=300),
    dict(id="bolt", s=30.0, e=36.5, bg="storm", clock="30,000 °C", char="cloud", pos=(560, 940, 380),
         props=with_thermo(bolt_props), look=(0, 0.5),
         narr="LIGHTNING heats air to about 30,000 °C. FIVE times the Sun's surface!", n_at=30.2,
         say="Sorry, Sun!", say_at=32.6, pitch=360),
    dict(id="core", s=36.5, e=43.0, bg="space", clock="15 MILLION °C", char="sun", pos=(560, 1060, 560),
         props=with_thermo(core_props), look=(0, -0.3),
         narr="Now go DEEP. The Sun's core: about 15 MILLION °C.", n_at=36.7,
         say="Top THAT!", say_at=39.2, pitch=300),
    dict(id="fusion", s=43.0, e=49.5, bg="office", clock="150 MILLION °C", props=with_thermo(tokamak),
         narr="Fusion reactors like ITER, which India helps build, aim for 150 MILLION °C.", n_at=43.2),
    dict(id="lhc", s=49.5, e=TW, bg="night", clock="5 TRILLION °C", char="kid", pos=(560, 1060, 360),
         props=with_thermo(ring_props), look=(0.5, 0),
         narr="The record: CERN's LHC, 2012. Smashed lead atoms hit over 5 TRILLION degrees.", n_at=49.7,
         say="HOTTEST thing EVER!", say_at=52.6, pitch=640),
    dict(id="twist", s=TW, e=63.0, bg="night", clock="WAIT...", char="penguin", pos=(540, 1080, 420),
         props=twist_props, twist=True, look=(0, -0.3),
         narr="Twist: the LHC's magnets are kept at -271.3 °C. COLDER than outer space!", n_at=56.4,
         say="Finally, MY kind of place!", say_at=59.2, pitch=560),
    dict(id="outro", s=63.0, e=68.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("sun", 300, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=68.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU CHASED", WHITE)], 140), 770, 0.75, "right"),
        (title([("THE HOTTEST", WHITE)], 130), 915, 1.05, "left"),
        (title([("temperature ", WHITE), ("EVER?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which shocked ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("the most?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("chai", 1), ("sun", 1), ("cloud", 1), ("penguin", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=63.0, t1=68.0, melody=True)],
    fx=[("bubbles", 10.8, 0.4, dict(dd=5.0)), ("rumble", 17.1, 0.6, dict(dd=5.0)), ("crash", 30.4, 0.6),
        ("crash", 31.7, 0.4), ("boom", 52.0, 0.8), ("wind", TW + 0.1, 0.4, dict(dd=5.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_hottest_temperature")
