#!/usr/bin/env python3
"""What if humans could hibernate? Facts: Himalayan brown bears in Lahaul, Himachal Pradesh hibernate through winter,
historically about November to May, now usually emerging mid-April (Sanctuary Nature Foundation). A captive black
bear's heart beat 40-50 times a minute in early fall and as few as 8 times a minute in deep hibernation; black bears
can go as long as 100 days without eating, drinking, urinating or defecating, and seem to avoid progressive bone
loss, though researchers don't yet know how (PBS NOVA 'Bear Essentials of Hibernation'). Lowest body temperature
recorded in a mammal: -2.9 C, Arctic ground squirrel (Guinness World Records; Barnes, Science 1989). ESA study:
hibernating crews on a 180-day Earth-Mars cruise could cut spacecraft mass by about a third; target is to reduce an
astronaut's basic metabolic rate by 75%; astronauts would need extra body fat before torpor (ESA 'Hibernating
astronauts would need smaller spacecraft', 2019). Twist: dwarf lemurs of Madagascar are primates that hibernate for
about seven months (Live Science 2013, Duke Lemur Center study)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 60.0
FUR = (150, 96, 60)
FUR_L = (206, 160, 118)
SQ = (196, 150, 96)
LEM = (170, 160, 150)

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

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def snow_bg():
    if "snow" not in _bgc:
        img = grad([(0, (120, 170, 220)), (0.6, (180, 210, 236)), (1, (220, 232, 246))], W, H)
        d = ImageDraw.Draw(img)
        for (x, h, w) in [(120, 520, 420), (520, 640, 520), (920, 500, 420)]:
            top = 1330 - h
            d.polygon([(x - w, 1330), (x, top), (x + w, 1330)], fill=(120, 130, 160), outline=OUTL)
            d.polygon([(x - w * 0.3, top + h * 0.3), (x, top), (x + w * 0.3, top + h * 0.3),
                       (x + w * 0.12, top + h * 0.24), (x, top + h * 0.32), (x - w * 0.14, top + h * 0.25)],
                      fill=WHITE)
        d.rectangle([0, 1320, W, H], fill=(96, 116, 156))
        d.rectangle([0, 1320, W, 1350], fill=(236, 242, 250))
        _bgc["snow"] = img
    return _bgc["snow"]

def den_bg():
    if "den" not in _bgc:
        img = grad([(0, (40, 30, 34)), (1, (70, 54, 50))], W, H)
        d = ImageDraw.Draw(img)
        d.ellipse([-200, 500, 1280, 1900], fill=(90, 70, 60))
        d.ellipse([-100, 640, 1180, 1800], fill=(60, 46, 42))
        d.rectangle([0, 1330, W, H], fill=(84, 66, 52))
        _bgc["den"] = img
    return _bgc["den"]

def lab_bg():
    if "lab" not in _bgc:
        img = grad([(0, (226, 236, 246)), (1, (196, 210, 228))], W, H)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1320, W, H], fill=(150, 160, 176))
        d.rectangle([0, 1310, W, 1330], fill=(110, 118, 134))
        _bgc["lab"] = img
    return _bgc["lab"]

def forest_bg():
    if "forest" not in _bgc:
        img = grad([(0, (120, 190, 160)), (1, (60, 120, 90))], W, H)
        d = ImageDraw.Draw(img)
        for x in (80, 300, 800, 1000):
            d.rectangle([x - 26, 600, x + 26, 1330], fill=(100, 70, 50), outline=OUTL, width=5)
            d.ellipse([x - 160, 380, x + 160, 700], fill=(50, 140, 80), outline=OUTL, width=5)
        d.rectangle([0, 1320, W, H], fill=(70, 110, 60))
        _bgc["forest"] = img
    return _bgc["forest"]

# ---------------------------------------------------------------- creatures
def zzz(frame, x, y, T, s=1.0):
    for k in range(3):
        ph = (T * 0.6 + k / 3) % 1
        put(frame, "Z", x + 50 * ph * s + k * 10, y - 160 * ph * s, int((40 + 30 * ph) * s), WHITE)

def bear(d, cx, cy, s, T, asleep=True):
    """Curled-up / sitting bear, body centred at (cx, cy); s ~ body half-width."""
    br = 1 + (0.03 * math.sin(T * 1.2) if asleep else 0)
    ow = max(3, int(s / 30))
    d.ellipse([cx - s * br, cy - s * 0.62 * br, cx + s * br, cy + s * 0.62 * br], fill=FUR, outline=OUTL, width=ow)
    # feet
    for fx in (-0.55, 0.45):
        d.ellipse([cx + fx * s - s * 0.2, cy + s * 0.38, cx + fx * s + s * 0.2, cy + s * 0.66], fill=FUR,
                  outline=OUTL, width=ow)
    # head
    hx, hy, hr = cx - s * 0.62, cy - s * 0.18, s * 0.44
    for ex in (-0.6, 0.55):
        er = hr * 0.32
        d.ellipse([hx + ex * hr - er, hy - hr * 0.85 - er, hx + ex * hr + er, hy - hr * 0.85 + er], fill=FUR,
                  outline=OUTL, width=ow)
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=FUR, outline=OUTL, width=ow)
    d.ellipse([hx - hr * 0.42, hy + hr * 0.05, hx + hr * 0.42, hy + hr * 0.6], fill=FUR_L, outline=OUTL, width=ow)
    d.ellipse([hx - hr * 0.14, hy + hr * 0.08, hx + hr * 0.14, hy + hr * 0.26], fill=OUTL)
    for ex in (-0.38, 0.38):
        x, y = hx + ex * hr, hy - hr * 0.2
        r = hr * 0.16
        if asleep:
            d.arc([x - r, y - r * 0.7, x + r, y + r * 0.7], 20, 160, fill=OUTL, width=max(3, ow))
        else:
            d.ellipse([x - r, y - r * 1.1, x + r, y + r * 1.1], fill=WHITE, outline=OUTL, width=max(2, ow - 1))
            d.ellipse([x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.6], fill=OUTL)

def squirrel(d, cx, cy, s, T):
    ow = max(3, int(s / 25))
    # curled tail
    d.ellipse([cx - s * 0.2, cy - s * 0.9, cx + s * 0.95, cy + s * 0.5], fill=(176, 130, 80), outline=OUTL, width=ow)
    d.ellipse([cx - s * 0.75, cy - s * 0.55, cx + s * 0.55, cy + s * 0.55], fill=SQ, outline=OUTL, width=ow)
    hx, hy, hr = cx - s * 0.45, cy - s * 0.05, s * 0.32
    d.ellipse([hx - hr * 0.5, hy - hr * 1.25, hx - hr * 0.05, hy - hr * 0.7], fill=SQ, outline=OUTL, width=ow)
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=SQ, outline=OUTL, width=ow)
    for ex in (-0.4, 0.3):
        x, y, r = hx + ex * hr, hy - hr * 0.1, hr * 0.2
        d.arc([x - r, y - r * 0.7, x + r, y + r * 0.7], 20, 160, fill=OUTL, width=max(3, ow))
    d.ellipse([hx - hr * 0.1, hy + hr * 0.3, hx + hr * 0.1, hy + hr * 0.45], fill=OUTL)
    # frost sparkles
    for k in range(6):
        a = k * 1.05 + T
        x, y = cx + math.cos(a) * s * 1.1, cy + math.sin(a) * s * 0.9
        d.line([(x - 10, y), (x + 10, y)], fill=WHITE, width=4)
        d.line([(x, y - 10), (x, y + 10)], fill=WHITE, width=4)

def lemur(d, cx, cy, s, T, asleep=True):
    ow = max(3, int(s / 25))
    # thick fat tail curled under
    d.ellipse([cx - s * 0.9, cy + s * 0.15, cx + s * 0.9, cy + s * 0.75], fill=(140, 128, 118), outline=OUTL,
              width=ow)
    d.ellipse([cx - s * 0.55, cy - s * 0.45, cx + s * 0.55, cy + s * 0.55], fill=LEM, outline=OUTL, width=ow)
    hx, hy, hr = cx, cy - s * 0.55, s * 0.4
    for ex in (-0.75, 0.75):
        er = hr * 0.3
        d.ellipse([hx + ex * hr - er, hy - hr * 0.8 - er, hx + ex * hr + er, hy - hr * 0.8 + er], fill=LEM,
                  outline=OUTL, width=ow)
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=LEM, outline=OUTL, width=ow)
    for ex in (-0.4, 0.4):
        x, y, r = hx + ex * hr, hy - hr * 0.05, hr * 0.3
        d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 50, 50))
        if asleep:
            d.arc([x - r * 0.7, y - r * 0.4, x + r * 0.7, y + r * 0.4], 20, 160, fill=WHITE, width=4)
        else:
            d.ellipse([x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6], fill=(250, 200, 90))
            d.ellipse([x - r * 0.25, y - r * 0.25, x + r * 0.25, y + r * 0.25], fill=OUTL)
    d.ellipse([hx - hr * 0.12, hy + hr * 0.4, hx + hr * 0.12, hy + hr * 0.56], fill=OUTL)

def heart(d, cx, cy, r, col=(230, 60, 80)):
    d.ellipse([cx - r, cy - r * 0.8, cx, cy + r * 0.2], fill=col, outline=OUTL, width=5)
    d.ellipse([cx, cy - r * 0.8, cx + r, cy + r * 0.2], fill=col, outline=OUTL, width=5)
    d.polygon([(cx - r * 0.97, cy - r * 0.15), (cx + r * 0.97, cy - r * 0.15), (cx, cy + r)], fill=col)
    d.line([(cx - r * 0.97, cy - r * 0.15), (cx, cy + r), (cx + r * 0.97, cy - r * 0.15)], fill=OUTL, width=5)

def cross(d, cx, cy, r):
    d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=(220, 40, 40), width=16)
    d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=(220, 40, 40), width=16)

# ---------------------------------------------------------------- props
def den_props(frame, d, T, sc):
    lt = T - sc["s"]
    # cave mouth
    d.chord([640, 980, 1100, 1560], 180, 360, fill=(40, 30, 30), outline=OUTL, width=8)
    q = ease_out(clamp((lt - 0.6) / 4.5))
    bear(d, 300 + 520 * q, 1200, 150, T, asleep=False)
    if lt > 0.5: top_label(frame, "HIMALAYAS, NOVEMBER", 380, YEL, 82)

def heart_props(frame, d, T, sc):
    lt = T - sc["s"]
    bear(d, 560, 1160, 230, T)
    zzz(frame, 380, 900, T)
    bpm = 45 - 37 * clamp((lt - 1.0) / 4.0)
    ph = (T * bpm / 60) % 1
    beat = 1 + 0.18 * max(0, 1 - ph * 6)
    heart(d, 830, 780, 90 * beat)
    put(frame, f"{int(round(bpm))} BEATS / MIN", 540, 500, 70, WHITE)
    if lt > 0.5: top_label(frame, "HEART SLOWS DOWN", 380, YEL, 88)

def plate(d, cx, cy):
    d.ellipse([cx - 80, cy - 40, cx + 80, cy + 40], fill=WHITE, outline=OUTL, width=6)
    d.ellipse([cx - 40, cy - 30, cx + 40, cy + 10], fill=(240, 180, 60), outline=OUTL, width=4)

def glass(d, cx, cy):
    d.polygon([(cx - 50, cy - 70), (cx + 50, cy - 70), (cx + 38, cy + 70), (cx - 38, cy + 70)], fill=(190, 230, 255),
              outline=OUTL)
    d.rectangle([cx - 42, cy - 20, cx + 42, cy + 66], fill=(110, 180, 240))

def toilet(d, cx, cy):
    d.rounded_rectangle([cx - 40, cy - 90, cx + 40, cy - 20], radius=10, fill=WHITE, outline=OUTL, width=6)
    d.ellipse([cx - 80, cy - 30, cx + 80, cy + 30], fill=WHITE, outline=OUTL, width=6)
    d.polygon([(cx - 50, cy + 20), (cx + 50, cy + 20), (cx + 30, cy + 80), (cx - 30, cy + 80)], fill=WHITE,
              outline=OUTL)

def noloo_props(frame, d, T, sc):
    lt = T - sc["s"]
    bear(d, 540, 1190, 200, T)
    zzz(frame, 400, 960, T)
    for k, (fn, x) in enumerate([(plate, 220), (glass, 540), (toilet, 860)]):
        if lt > 0.8 + k * 0.6:
            fn(d, x, 680)
            if lt > 1.1 + k * 0.6: cross(d, x, 680, 70)
    if lt > 0.5: top_label(frame, "100 DAYS", 380, YEL, 120)

def bones_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 1.0) / 1.0)
    bear(d, 540, 1150, 220, T, asleep=q < 0.5)
    # a bone that stays strong
    if lt > 2.0:
        x, y = 540, 700
        d.rounded_rectangle([x - 150, y - 26, x + 150, y + 26], radius=20, fill=WHITE, outline=OUTL, width=6)
        for ex in (-150, 150):
            for ey in (-28, 28):
                d.ellipse([x + ex - 36, y + ey - 36, x + ex + 36, y + ey + 36], fill=WHITE, outline=OUTL, width=6)
        d.rounded_rectangle([x - 150, y - 26, x + 150, y + 26], radius=20, fill=WHITE)
    if lt > 0.5: top_label(frame, "SPRING: WAKE UP!", 380, YEL, 88)

def thermo(d, cx, top, bot, frac, col=(80, 160, 240)):
    d.rounded_rectangle([cx - 30, top, cx + 30, bot], radius=30, fill=WHITE, outline=OUTL, width=6)
    d.ellipse([cx - 55, bot - 40, cx + 55, bot + 70], fill=col, outline=OUTL, width=6)
    lev = bot - (bot - top - 30) * frac
    d.rectangle([cx - 16, lev, cx + 16, bot], fill=col)

def squirrel_props(frame, d, T, sc):
    lt = T - sc["s"]
    squirrel(d, 420, 1150, 220, T)
    f = 1 - 0.85 * clamp((lt - 0.8) / 3.5)
    thermo(d, 860, 560, 1080, f)
    t = 37 - 39.9 * clamp((lt - 0.8) / 3.5)
    put(frame, f"{t:.1f} C", 860, 1180, 70, WHITE)
    if lt > 0.5: top_label(frame, "ARCTIC GROUND SQUIRREL", 380, YEL, 74)

def pod(d, cx, cy, T, k):
    d.rounded_rectangle([cx - 120, cy - 60, cx + 120, cy + 60], radius=60, fill=(220, 236, 250), outline=OUTL,
                        width=6)
    d.rounded_rectangle([cx - 90, cy - 40, cx + 40, cy + 40], radius=40, fill=(150, 200, 240))
    d.ellipse([cx - 80, cy - 30, cx - 20, cy + 30], fill=(250, 214, 180), outline=OUTL, width=4)
    d.arc([cx - 70, cy - 10, cx - 50, cy + 4], 20, 160, fill=OUTL, width=3)
    d.arc([cx - 50, cy - 10, cx - 30, cy + 4], 20, 160, fill=OUTL, width=3)

def space_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "rocket", 300, 900, 380, T)
    for k in range(3):
        if lt > 1.0 + k * 0.5: pod(d, 760, 720 + k * 170, T, k)
    if lt > 3.0:
        x, r = 860, 70
        d.ellipse([x - r, 1220 - r, x + r, 1220 + r], fill=(214, 96, 60), outline=OUTL, width=6)
        put(frame, "MARS", x, 1300, 50, WHITE)
    if lt > 0.5: top_label(frame, "1/3 LIGHTER SHIP", 380, YEL, 92)

def fat_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = int(clamp((lt - 0.8) / 4.0) * 10)
    for k in range(n):
        x = 700 + (k % 4) * 90 - (k // 4) * 45 + (k // 4) * 0
        y = 1240 - (k // 4) * 80
        mini(frame, "ladoo", x, y, 110, T)
    put(frame, "ENERGY USE -75%", 540, 520, 76, WHITE)
    if lt > 0.5: top_label(frame, "STEP 1: BULK UP", 380, YEL, 96)

def calendar(d, cx, cy, txt_frame, T, month):
    d.rounded_rectangle([cx - 150, cy - 140, cx + 150, cy + 140], radius=20, fill=WHITE, outline=OUTL, width=7)
    d.rectangle([cx - 150, cy - 140, cx + 150, cy - 70], fill=(220, 60, 70), outline=OUTL, width=7)
    put(txt_frame, month, cx, cy - 20, 66, (40, 40, 60))

def you_props(frame, d, T, sc):
    lt = T - sc["s"]
    months = ["NOV", "DEC", "JAN", "FEB", "MAR", "APR"]
    m = months[min(5, int(clamp((lt - 0.8) / 4.5) * 6))]
    calendar(d, 820, 720, frame, T, m)
    zzz(frame, 300, 1080, T)
    if lt > 0.5: top_label(frame, "SNOOZE SEASON", 380, YEL, 96)

def lemur_props(frame, d, T, sc):
    lt = T - sc["s"]
    # tree hollow
    d.rounded_rectangle([580, 760, 1000, 1330], radius=120, fill=(110, 76, 52), outline=OUTL, width=7)
    d.ellipse([640, 880, 940, 1260], fill=(50, 34, 26), outline=OUTL, width=6)
    lemur(d, 790, 1110, 150, T, asleep=lt < 4.5)
    if lt < 4.5: zzz(frame, 880, 920, T, 0.8)
    if lt > 0.5: top_label(frame, "DWARF LEMUR", 380, YEL, 110)
    if lt > 1.5: put(frame, "~7 MONTHS ASLEEP", 540, 500, 70, WHITE)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="den", s=4.0, e=11.0, bg_fn=lambda T: snow_bg(), clock="RIGHT NOW", props=den_props,
         narr="Right now in the HIMALAYAS, brown bears are heading into dens to sleep till SPRING.",
         n_at=4.2, narr_y=1600),
    dict(id="heart", s=11.0, e=18.0, bg_fn=lambda T: den_bg(), clock="DEEP SLEEP", props=heart_props,
         narr="A black bear's heart can slow from about 45 BEATS a minute to just 8.", n_at=11.2,
         narr_y=1600),
    dict(id="noloo", s=18.0, e=25.0, bg_fn=lambda T: den_bg(), clock="NO BREAKS", props=noloo_props,
         narr="Black bears can go up to 100 DAYS with no food, no water and NO TOILET breaks.", n_at=18.2,
         narr_y=1600),
    dict(id="bones", s=25.0, e=32.0, bg_fn=lambda T: snow_bg(), clock="APRIL", props=bones_props,
         narr="They wake up without their BONES wasting away, and scientists still don't know HOW.",
         n_at=25.2, narr_y=1600),
    dict(id="squirrel", s=32.0, e=39.0, bg_fn=lambda T: snow_bg(), clock="RECORD", props=squirrel_props,
         narr="An Arctic ground squirrel's body can cool to MINUS 2.9 degrees, colder than ICE, and survive.",
         n_at=32.2, narr_y=1600),
    dict(id="space", s=39.0, e=46.0, bg="space", clock="TO MARS", props=space_props,
         narr="A EUROPEAN SPACE AGENCY study found sleeping astronauts could make a Mars ship a THIRD lighter.",
         n_at=39.2, narr_y=1600),
    dict(id="fat", s=46.0, e=53.0, bg="living", clock="BUT FIRST", props=fat_props, char="kid",
         pos=(280, 1120, 360), state="puff", look=(0.6, 0),
         narr="You'd need extra body FAT first, and your energy use would have to drop by 75%.", n_at=46.2,
         narr_y=1600, say="Ladoo DIET!", say_at=49.6, pitch=440),
    dict(id="you", s=53.0, e=TW, bg="bedroom", clock="YOU", props=you_props, char="kid", pos=(370, 1140, 280),
         look=(0, 0.3),
         narr="You'd snooze from NOVEMBER to APRIL and skip the whole WINTER.", n_at=53.2, narr_y=1600),
    dict(id="twist", s=TW, e=67.0, bg_fn=lambda T: forest_bg(), clock="PLOT TWIST", props=lemur_props, twist=True,
         narr="Twist: a PRIMATE cousin of ours already does it. Madagascar's dwarf lemurs sleep about 7 MONTHS!",
         n_at=TW + 0.2, narr_y=1600),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        bear(d, 560, 1300, 170 * p, T)
        if T > 2.2: zzz(frame, 380, 1150, T)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("HUMANS COULD", WHITE)], 120), 730, 0.75, "right"),
        (title([("HIBERNATE?", YEL)], 150), 880, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("If ", WHITE), ("YOU", YEL), (" could hibernate,", WHITE)], 84), 470, 0.15),
                      (title([("which month would you skip?", YEL)], 74), 600, 0.45)],
               row=[("kid", 1), ("ladoo", 1), ("moon", 1), ("rocket", 1), ("earth", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, melody=True),
           dict(t0=11.0, t1=18.0, drums=False, minor=True), dict(t0=18.0, t1=32.0),
           dict(t0=32.0, t1=46.0, melody=True), dict(t0=46.0, t1=TW - 0.15, drums=False),
           dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=11.0, dur=7.0, g=0.1)],
    fx=[("wind", 4.2, 0.15, dict(dd=6.5)), ("heartbeat", 12.0, 0.35, dict(dd=5.5, bpm=20)),
        ("pop", 19.0, 0.2), ("pop", 19.6, 0.2), ("pop", 20.2, 0.2), ("ding", 27.0, 0.15),
        ("wind", 32.2, 0.12, dict(dd=6.5)), ("whoosh", 40.0, 0.3), ("pop", 47.5, 0.15), ("pop", 49.0, 0.15),
        ("tick", 55.0, 0.2), ("tick", 56.5, 0.2), ("tick", 58.0, 0.2), ("pop", 64.6, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_humans_could_hibernate")
