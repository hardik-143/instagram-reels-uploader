#!/usr/bin/env python3
"""What if you chased the coldest temperature ever? A temperature ladder going down:
freezer -18 °C; dry ice -78 °C and liquid nitrogen -196 °C (University of Illinois DRS cryogen safety table);
Vostok Station, Antarctica, -89.2 °C on 21 July 1983 (Guinness World Records); Tamil Nadu (Apr 2024) and Karnataka
(May 2024) banned liquid nitrogen in served food / 'smoke biscuits' (South First, ETV Bharat); Triton -235 °C,
Voyager 2 flyby 1989 (The Planetary Society); Boomerang Nebula ~1 K (~-272 °C), 5,000 light-years away, colder than
the 2.8 K Big Bang afterglow (ALMA/NRAO); first Bose-Einstein condensate 5 June 1995 at 170 nanokelvin (JILA),
based on Kolkata-born S. N. Bose's 1924 work extended by Einstein (New World Encyclopedia); lab record 38 picokelvin,
Bremen Drop Tower, 2021 (phys.org).
Twist: at normal pressure helium never solidifies, even near absolute zero; it needs ~25 atmospheres (Chemicool)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 56.0
ICE = (170, 220, 255)

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

# ---------------------------------------------------------------- thermometer, level FALLS scene by scene
ORDER = ["freezer", "dryice", "vostok", "nitro", "triton", "nebula", "bose", "record"]
LEV = dict(zip(ORDER, [0.82, 0.68, 0.56, 0.44, 0.32, 0.2, 0.1, 0.03]))
PREV = dict(zip(ORDER, [0.95] + [LEV[o] for o in ORDER[:-1]]))

def thermo(frame, d, T, sc):
    lt = T - sc["s"]
    lv = PREV[sc["id"]] + (LEV[sc["id"]] - PREV[sc["id"]]) * ease_out(clamp(lt / 1.2))
    x, top, bot = 80, 480, 1200
    d.rounded_rectangle([x - 26, top, x + 26, bot], 26, fill=(250, 250, 255), outline=OUTL, width=5)
    d.ellipse([x - 48, bot - 30, x + 48, bot + 66], fill=(60, 140, 240), outline=OUTL, width=5)
    yl = bot - (bot - top - 20) * lv
    d.rounded_rectangle([x - 14, yl, x + 14, bot + 10], 14, fill=(60, 140, 240))
    for k in range(1, 8):
        yy = bot - (bot - top) * k / 8
        d.line([(x + 26, yy), (x + 44, yy)], fill=OUTL, width=4)

def with_thermo(fn=None):
    def p(frame, d, T, sc):
        if fn: fn(frame, d, T, sc)
        thermo(frame, d, T, sc)
    return p

def flake(d, x, y, r=18, col=WHITE, w=5):
    for ang in (0, 60, 120):
        a = math.radians(ang)
        d.line([(x - r * math.cos(a), y - r * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))], fill=col, width=w)

# ---------------------------------------------------------------- scene props
def freezer(frame, d, T, sc):
    lt = T - sc["s"]
    # ice cubes stacked to the right of the kid
    for i, (x, y) in enumerate([(820, 1200), (920, 1200), (870, 1110)]):
        p = ease_back(clamp((lt - 0.4 - i * 0.25) / 0.4))
        if p <= 0: continue
        s = 44 * p
        d.rounded_rectangle([x - s, y - s, x + s, y + s], 14, fill=(200, 235, 255), outline=OUTL, width=5)
        d.line([(x - s * 0.5, y - s * 0.5), (x - s * 0.1, y - s * 0.5)], fill=WHITE, width=6)

def dryice(frame, d, T, sc):
    lt = T - sc["s"]
    d.rounded_rectangle([340, 1090, 740, 1250], 20, fill=(235, 240, 250), outline=OUTL, width=6)
    for k in range(9):   # fog rolling off
        ph = (lt * 0.35 + k / 9) % 1.0
        x = 360 + (k % 5) * 90 + 120 * ph * (1 if k % 2 else -1)
        y = 1080 - 40 * math.sin(ph * 3) + 160 * ph
        r = 40 + 50 * ph
        a = int(170 * (1 - ph))
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(245, 250, 255, a))

def vostok(frame, d, T, sc):
    lt = T - sc["s"]
    d.polygon([(0, 1320), (300, 1180), (620, 1240), (1080, 1150), (1080, 1400), (0, 1400)], fill=(235, 245, 255),
              outline=OUTL)
    for k in range(14):
        ph = (lt * 0.5 + k / 14) % 1.0
        flake(d, 140 + (k * 137) % 860, 420 + ph * 820, 12, WHITE, 4)

def nitro(frame, d, T, sc):
    lt = T - sc["s"]
    # dewar flask on the right
    d.rounded_rectangle([760, 980, 960, 1260], 30, fill=(180, 190, 210), outline=OUTL, width=6)
    d.rectangle([800, 950, 920, 990], fill=(140, 150, 170), outline=OUTL, width=5)
    for k in range(4):
        ph = (lt * 0.5 + k / 4) % 1.0
        x = 860 + 30 * math.sin(lt * 2 + k); y = 930 - ph * 160
        r = 26 + 30 * ph
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(245, 250, 255, int(160 * (1 - ph))))

def nitro_after(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 2.0:   # shards fly off the flower
        q = clamp((lt - 2.0) / 1.2)
        for k in range(8):
            a = k * 0.8 + 0.3
            x = 430 + math.cos(a) * 260 * q; y = 960 + math.sin(a) * 200 * q + 200 * q * q
            d.polygon([(x, y - 16), (x + 12, y + 10), (x - 12, y + 10)], fill=ICE, outline=OUTL)

def triton(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, r = 540, 1050, 330
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(225, 205, 205), outline=OUTL, width=6)
    for (x, y, rr) in [(-120, -80, 50), (90, 40, 70), (-40, 160, 40), (160, -150, 35)]:
        d.ellipse([cx + x - rr, cy + y - rr, cx + x + rr, cy + y + rr], fill=(205, 180, 185))
    for k in range(2):   # nitrogen geysers
        gx = cx - 60 + k * 180; gy = cy - r + 40 + k * 30
        h = 160 + 30 * math.sin(lt * 3 + k)
        d.line([(gx, gy), (gx + 10, gy - h)], fill=(80, 70, 70), width=10)
        d.ellipse([gx + 10 - 30, gy - h - 20, gx + 10 + 30, gy - h + 20], fill=(110, 100, 100))

def nebula(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1050
    for s, col in [(1.0, (90, 120, 200)), (0.7, (140, 170, 240)), (0.4, (200, 220, 255))]:
        for sgn in (1, -1):
            w = 300 * s * (1 + 0.04 * math.sin(lt * 2))
            d.polygon([(cx, cy), (cx + sgn * w, cy - 150 * s), (cx + sgn * w * 1.15, cy),
                       (cx + sgn * w, cy + 150 * s)], fill=col)
    glow(frame, cx, cy, 120, (255, 255, 240), 1.0)
    if lt > 1.5:
        top_label(frame, "COLDER THAN SPACE", 700, ICE, 62)

def atoms(frame, d, T, sc):
    lt = T - sc["s"]
    q = ease_out(clamp((lt - 1.0) / 2.5))   # spread atoms collapse into one blob
    cx, cy = 540, 1150
    for k in range(14):
        a = k * 2.399
        r0 = 120 + (k * 53) % 260
        x = cx + math.cos(a + lt * 2 * (1 - q)) * r0 * (1 - q); y = cy + math.sin(a + lt * 2 * (1 - q)) * r0 * 0.6 * (1 - q)
        rr = 26
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 160, 80), outline=OUTL, width=4)
    if q > 0.6:
        glow(frame, cx, cy, 150, (255, 200, 120), 0.9 * q)

def tower(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([650, 840, 790, 1330], fill=(200, 205, 220), outline=OUTL, width=6)
    for k in range(7):
        y = 880 + k * 70
        d.line([(650, y), (790, y)], fill=OUTL, width=3)
    y = 870 + ((lt * 0.45) % 1.0) ** 2 * 420
    glow(frame, 720, y, 70, (150, 230, 255), 1.0)
    d.ellipse([700, y - 20, 740, y + 20], fill=ICE, outline=OUTL, width=4)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a flask of liquid helium that refuses to freeze
    d.rounded_rectangle([700, 1000, 940, 1280], 40, fill=(220, 230, 245), outline=OUTL, width=6)
    wy = 1120 + 10 * math.sin(lt * 4)
    d.rectangle([712, wy, 928, 1268], fill=(150, 200, 255))
    pts = [(712 + i * 12, wy + 8 * math.sin(lt * 5 + i * 0.6)) for i in range(19)]
    d.line(pts, fill=OUTL, width=4)
    l = label("He", 70, WHITE); comp(frame, l, 820 - l.width / 2, 1020)
    if lt > 3.0:
        top_label(frame, "STILL LIQUID!", 380, ICE, 66)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="freezer", s=4.0, e=10.5, bg="day", clock="-18 °C", char="kid", pos=(520, 1080, 460),
         props=with_thermo(freezer), look=(0.5, 0),
         narr="Start in your FREEZER: about -18 °C. Kulfi sets, ice cubes form.", n_at=4.2,
         say="Kulfi time!", say_at=7.2, pitch=640),
    dict(id="dryice", s=10.5, e=17.0, bg="night", clock="-78 °C", props=with_thermo(dryice),
         narr="Colder: DRY ICE, frozen carbon dioxide, at -78 °C. It turns straight into FOG.", n_at=10.7),
    dict(id="vostok", s=17.0, e=23.5, bg="night", clock="-89.2 °C", char="penguin", pos=(540, 1060, 420),
         props=with_thermo(vostok), look=(0, -0.3),
         narr="Earth's coldest air ever: -89.2 °C at VOSTOK, Antarctica, 1983.", n_at=17.2,
         say="Even I don't live HERE!", say_at=19.8, pitch=560),
    dict(id="nitro", s=23.5, e=30.0, bg="office", clock="-196 °C", char="flower", pos=(430, 1060, 380),
         props=with_thermo(nitro), props_after=nitro_after, look=(0.5, 0),
         narr="LIQUID NITROGEN: -196 °C. Tamil Nadu and Karnataka BANNED it in 'smoke biscuits'.", n_at=23.7,
         say="It can burn you INSIDE!", say_at=26.6, pitch=520),
    dict(id="triton", s=30.0, e=36.5, bg="space", clock="-235 °C", props=with_thermo(triton),
         narr="Neptune's moon TRITON: about -235 °C. Voyager 2 saw it in 1989.", n_at=30.2),
    dict(id="nebula", s=36.5, e=43.0, bg="space", clock="-272 °C", props=with_thermo(nebula),
         narr="The BOOMERANG Nebula, 5,000 light-years away: -272 °C. Colder than the Big Bang's glow!", n_at=36.7),
    dict(id="bose", s=43.0, e=49.5, bg="office", clock="170 BILLIONTHS", char="kid", pos=(250, 1100, 300),
         props=with_thermo(atoms), look=(0.6, 0),
         narr="1995 lab: atoms at 170 BILLIONTHS of a degree merged into one 'super atom'.", n_at=43.2,
         say="Kolkata's BOSE predicted it!", say_at=46.0, pitch=640),
    dict(id="record", s=49.5, e=TW, bg="night", clock="38 TRILLIONTHS", char="kid", pos=(380, 1080, 360),
         props=with_thermo(tower), look=(0.6, -0.3),
         narr="2021: a German lab hit 38 TRILLIONTHS of a degree above ABSOLUTE ZERO.", n_at=49.7, say="Almost -273.15 °C!", say_at=52.8, pitch=640),
    dict(id="twist", s=TW, e=63.0, bg="night", clock="WAIT...", char="penguin", pos=(400, 1080, 400),
         props=twist_props, twist=True, look=(0.6, 0),
         narr="Twist: at normal pressure, HELIUM never freezes. Not even near ABSOLUTE ZERO!", n_at=56.4,
         say="Un-freezable?!", say_at=59.4, pitch=560),
    dict(id="outro", s=63.0, e=68.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("penguin", 300, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=68.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU CHASED", WHITE)], 140), 770, 0.75, "right"),
        (title([("THE COLDEST", WHITE)], 130), 915, 1.05, "left"),
        (title([("temperature ", WHITE), ("EVER?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which shocked ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("the most?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("penguin", 1), ("flower", 1), ("moon", 1), ("earth", 0)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=63.0, t1=68.0, melody=True)],
    fx=[("wind", 10.8, 0.35, dict(dd=5.0)), ("wind", 17.2, 0.5, dict(dd=5.5)), ("crash", 25.6, 0.5),
        ("rumble", 30.3, 0.4, dict(dd=5.0)), ("bubbles", 43.4, 0.3, dict(dd=5.0)), ("whoosh", 50.2, 0.5),
        ("wind", TW + 0.1, 0.35, dict(dd=5.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_coldest_temperature")
