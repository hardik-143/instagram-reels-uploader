#!/usr/bin/env python3
"""What if you had a dog's nose? Facts (PBS NOVA 'Dogs' Dazzling Sense of Smell'): dogs have up to 300 million
olfactory receptors vs about 6 million in humans; their sense of smell is estimated at 10,000 to 100,000 times as
acute; a dog could detect a teaspoon of sugar in a million US gallons (~3.8 million litres, ~1.5 Olympic pools at
2.5 million litres) of water; the brain area devoted to analysing smells is proportionally 40 times greater; about
12 percent of inhaled air detours into a recessed olfactory area; exhaled air leaves through the side slits of the
nose; nostrils move independently and help a dog tell which nostril an odour arrived in. Twist (Smithsonian 2017,
citing Matthias Laska): of 15 odorants with thresholds measured in both, humans were more sensitive to 5, all
components of fruit or flower odours."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
BLUE = (70, 150, 230)

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

def dog_nose(d, x, y, s):
    d.ellipse([x - 0.9 * s, y - 0.6 * s, x + 0.9 * s, y + 0.6 * s], fill=(30, 22, 30), outline=OUTL, width=4)
    d.ellipse([x - 0.45 * s, y - 0.4 * s, x - 0.05 * s, y - 0.15 * s], fill=(110, 100, 120))

def puff(d, x, y, r, col, a=255):
    for dx, dy, k in ((-0.6, 0.1, 0.7), (0, -0.2, 1.0), (0.6, 0.1, 0.7)):
        rr = r * k
        d.ellipse([x + dx * r - rr, y + dy * r - rr, x + dx * r + rr, y + dy * r + rr], fill=col + (a,))

# ---------------------------------------------------------------- props
def wake_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "kid", 540, 1000, 520, T, 1, (0, 0))
    if lt > 1.0:
        p = min(ease_back(clamp((lt - 1.0) / 0.5)), 1.1)
        dog_nose(ImageDraw.Draw(frame), 540, 1000 + 0.1 * 520, 46 * p + 1)
    if lt > 1.8:
        top_label(frame, "BOOP!", 400, YEL, 100)

def receptors_props(frame, d, T, sc):
    lt = T - sc["s"]
    base = 1290
    mini(frame, "kid", 300, 560, 200, T)
    mini(frame, "dog", 780, 560, 210, T)
    p1 = ease_out(clamp((lt - 0.6) / 0.8)); p2 = ease_out(clamp((lt - 2.2) / 1.6))
    h1 = 600 * 6 / 300 * p1 + 4; h2 = 600 * p2 + 4
    d.rounded_rectangle([220, base - h1, 380, base], radius=10, fill=WHITE, outline=OUTL, width=5)
    d.rounded_rectangle([700, base - h2, 860, base], radius=10, fill=YEL, outline=OUTL, width=5)
    if lt > 1.2: lab_at(frame, "6 MILLION", 300, base - h1 - 50, WHITE, 52)
    if lt > 3.6: lab_at(frame, "300 MILLION", 780, 715, YEL, 56)
    if lt > 0.3: top_label(frame, "SMELL RECEPTORS", 380, WHITE, 64)

def sugar_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.4) / 0.8))
    # one full pool + half a pool
    for x0, w in ((90, 560), (690, 300)):
        ww = w * p
        d.rounded_rectangle([x0, 900, x0 + max(ww, 4), 1240], radius=16, fill=(60, 140, 220), outline=OUTL, width=6)
        for y in (960, 1040, 1120, 1200):
            if ww > 30: d.line([(x0 + 14, y), (x0 + ww - 14, y)], fill=(140, 200, 245), width=4)
    if lt > 1.2: lab_at(frame, "~1.5 OLYMPIC POOLS", 540, 830, WHITE, 60)
    if lt > 2.0:
        q = ease_back(clamp((lt - 2.0) / 0.4))
        r = 22 * q + 1
        d.ellipse([370 - r, 1060 - r, 370 + r, 1060 + r], fill=WHITE, outline=OUTL, width=4)
        lab_at(frame, "1 SPOON OF SUGAR", 540, 1295, YEL, 52)
    if lt > 3.4:
        mini(frame, "dog", 900, 600, 220 + 10 * math.sin(T * 8), T, 1, (-0.3, 0.3))
        top_label(frame, "SNIFF SNIFF", 400, YEL, 72)

def brain(d, cx, cy, r, frac, col):
    d.ellipse([cx - r, cy - r * 0.75, cx + r, cy + r * 0.75], fill=(240, 170, 190), outline=OUTL, width=6)
    a = 360 * frac
    d.pieslice([cx - r, cy - r * 0.75, cx + r, cy + r * 0.75], 180, 180 + a, fill=col, outline=OUTL, width=4)

def brain_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "kid", 300, 700, 240, T)
    mini(frame, "dog", 780, 700, 250, T)
    p = ease_out(clamp((lt - 1.0) / 1.5))
    brain(d, 300, 1020, 170, 0.006, WHITE)
    brain(d, 780, 1020, 170, 0.006 + 0.24 * p, YEL)
    lab_at(frame, "YOU", 300, 1240, WHITE, 52)
    lab_at(frame, "DOG", 780, 1240, YEL, 52)
    if lt > 2.8: top_label(frame, "40x BIGGER (FOR ITS SIZE)", 400, YEL, 58)
    if lt > 1.0: lab_at(frame, "(NOT TO SCALE)", 540, 1300, WHITE, 36)

def air_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1000
    # nose tube: air comes from the left, most goes down to the lungs, a bit goes up to the smell room
    d.rounded_rectangle([600, 640, 960, 820], radius=30, fill=(200, 80, 110), outline=OUTL, width=6)
    lab_at(frame, "SMELL ROOM", 780, 730, WHITE, 44)
    d.rectangle([120, 960, 760, 1060], fill=(255, 210, 200), outline=OUTL, width=6)
    d.rectangle([660, 820, 760, 960], fill=(255, 210, 200), outline=OUTL, width=6)
    d.rectangle([665, 955, 755, 965], fill=(255, 210, 200))
    d.rectangle([760, 960, 900, 1060], fill=(255, 210, 200), outline=OUTL, width=6)
    d.rectangle([755, 965, 765, 1055], fill=(255, 210, 200))
    lab_at(frame, "TO LUNGS", 900, 1120, WHITE, 44)
    lab_at(frame, "SNIFF IN", 220, 900, WHITE, 44)
    for k in range(25):
        t = (lt * 0.6 + k / 25.0) % 1.0
        up = (k % 8 == 0)
        if t < 0.6:
            x, y = 130 + (700 - 130) * (t / 0.6), 1010
        elif up:
            x, y = 710, 1010 - 260 * ((t - 0.6) / 0.4)
        else:
            x, y = 700 + 200 * ((t - 0.6) / 0.4), 1010
        r = 12
        d.ellipse([x - r, y - r, x + r, y + r], fill=YEL if up else WHITE, outline=OUTL, width=3)
    if lt > 2.2: top_label(frame, "ABOUT 12% OF EACH SNIFF", 400, YEL, 62)

def slit_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, B = 540, 1000, 560
    mini(frame, "dog", cx, cy, B, T, 1, (0, 0))
    nx, ny = cx, cy + 0.055 * B
    dd = ImageDraw.Draw(frame)
    for k in range(10):
        t = (lt * 0.8 + k / 10.0) % 1.0
        side = -1 if k % 2 else 1
        if (int(lt * 0.8 + k / 10.0)) % 2 == 0:
            x, y = nx + side * 40, ny - 260 + 230 * t   # coming in from the front
            col = WHITE
        else:
            x, y = nx + side * (60 + 260 * t), ny + 30 + 80 * t  # out the side slits
            col = (170, 200, 230)
        r = 12
        dd.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=OUTL, width=3)
    if lt > 1.5: top_label(frame, "OUT THROUGH THE SIDE SLITS", 400, YEL, 56)

def nostril_props(frame, d, T, sc):
    lt = T - sc["s"]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    p = ease_out(clamp((lt - 0.4) / 2.0))
    for k in range(4):
        x = 120 + 90 * k * p; y = 1000 + 30 * math.sin(T * 3 + k)
        puff(ld, x, y, 40 + 10 * k, (150, 230, 140), 170)
    frame.alpha_composite(lay)
    if lt > 0.6:
        mini(frame, "samosa", 110, 860, 150, T)
    if lt > 2.6:
        lab_at(frame, "LEFT NOSTRIL: STRONGER!", 540, 1290, YEL, 52)

def sniffer_props(frame, d, T, sc):
    lt = T - sc["s"]
    for i, (x, col) in enumerate(((220, (220, 90, 80)), (540, (80, 140, 220)), (860, (240, 180, 60)))):
        d.rounded_rectangle([x - 110, 1180, x + 110, 1330], radius=18, fill=col, outline=OUTL, width=6)
        d.rectangle([x - 40, 1160, x + 40, 1180], fill=(60, 60, 70), outline=OUTL, width=4)
    if lt > 3.0:
        q = ease_back(clamp((lt - 3.0) / 0.4))
        top_label(frame, "FOUND IT!", 400, YEL, int(70 + 30 * q))
        d.ellipse([860 - 150, 1150, 860 + 150, 1360], outline=YEL, width=10)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # banana + flower vs dog
    mini(frame, "dog", 540, 900, 300, T, 1, (0, 0.3))
    if lt > 0.8:
        q = ease_back(clamp((lt - 0.8) / 0.5))
        bx, by = 230, 1180
        d.arc([bx - 110 * q, by - 80 * q, bx + 110 * q, by + 80 * q], 10, 170, fill=(250, 220, 60), width=int(34 * q) + 1)
        mini(frame, "flower", 850, 1130, 240 * q + 2, T)
    if lt > 1.8:
        top_label(frame, "HUMANS WIN 5 OF 15", 400, YEL, 72)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wake", s=4.0, e=11.0, bg="bedroom", clock="7:00 AM", props=wake_props,
         narr="You wake up and your nose has turned into a DOG'S NOSE.", n_at=4.2),
    dict(id="receptors", s=11.0, e=18.0, bg="gully", clock="SMELL POWER", props=receptors_props,
         narr="You had about 6 MILLION smell receptors. A dog has up to 300 MILLION.", n_at=11.2,
         narr_y=1560),
    dict(id="sugar", s=18.0, e=25.0, bg="day", clock="SUPER SNIFF", props=sugar_props,
         narr="Now you could smell ONE SPOON of sugar in about 1.5 OLYMPIC POOLS.", n_at=18.2,
         narr_y=1530),
    dict(id="brain", s=25.0, e=32.0, bg="night", clock="BRAIN UPGRADE", props=brain_props,
         narr="The smell part of a dog's brain is about 40 TIMES bigger, for its size.", n_at=25.2,
         narr_y=1530),
    dict(id="air", s=32.0, e=39.0, bg="space", clock="SECRET ROOM", props=air_props,
         narr="About 12% of each sniff takes a DETOUR into a special smelling chamber.", n_at=32.2,
         narr_y=1500),
    dict(id="slits", s=39.0, e=46.0, bg="gully", clock="NONSTOP", props=slit_props,
         narr="You'd breathe OUT through side SLITS, so fresh smells keep flowing IN.", n_at=39.2,
         narr_y=1500),
    dict(id="nostril", s=46.0, e=TW, bg="gully", clock="GPS NOSE", props=nostril_props, char="dog",
         pos=(700, 980, 380), look=(-0.6, 0),
         narr="Each nostril sniffs on its own, helping you tell WHICH SIDE a smell is coming from.", n_at=46.2,
         narr_y=1500, say="SAMOSA, LEFT side!", say_at=48.8, pitch=330, bubble_y=640),
    dict(id="twist", s=TW, e=60.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: in tests, HUMANS beat dogs on 5 of 15 smells, mostly FRUITY and FLOWERY ones!",
         n_at=TW + 0.2, narr_y=1500),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        mini(frame, "dog", 540, 1240, 300 * p + 2, T)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU HAD A", WHITE)], 130), 690, 0.75, "right"),
        (title([("DOG'S NOSE?", YEL)], 160), 830, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What smell would ", WHITE)], 92), 470, 0.15),
                      (title([("YOU", YEL), (" follow first?", WHITE)], 96), 600, 0.45)],
               row=[("kid", 1), ("dog", 1), ("samosa", 1), ("chai", 1), ("dog", "wink")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=39.0), dict(t0=39.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("pop", 5.2, 0.3), ("ding", 14.6, 0.2), ("pop", 20.2, 0.3), ("ding", 28.0, 0.2),
        ("whoosh", 34.5, 0.2), ("wind", 39.5, 0.15, dict(dd=5.0)), ("ding", 48.8, 0.2), ("pop", TW + 1.0, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_had_a_dogs_nose")
