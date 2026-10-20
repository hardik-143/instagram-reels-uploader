#!/usr/bin/env python3
"""What if the oceans disappeared for 5 seconds? 97% of water, 3.7 km seafloor, Challenger Deep, Marine Drive, oxygen."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

OFF = 11.0     # oceans vanish
BACK = 45.0    # oceans return (twist)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=360, col=YEL, size=60):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def abyss():
    """The open ocean with the water gone: an empty, darkening canyon with rock walls."""
    if "abyss" not in _cache:
        y = np.linspace(0, 1, H)[:, None]
        top = np.array([70, 90, 120]); bot = np.array([8, 8, 18])
        a = (top * (1 - y[..., None]) + bot * y[..., None]).astype(np.uint8)
        a = np.broadcast_to(a, (H, W, 3)).copy()
        img = Image.fromarray(a).convert("RGBA"); d = ImageDraw.Draw(img)
        rng = np.random.default_rng(3)
        for side in (0, 1):
            pts = [(0 if side == 0 else W, 0)]
            for yy in range(0, H + 80, 80):
                x = 90 + 60 * math.sin(yy * 0.01 + side) + rng.uniform(-20, 20)
                pts.append((x if side == 0 else W - x, yy))
            pts.append((0 if side == 0 else W, H))
            d.polygon(pts, fill=(78, 58, 48))
        for _ in range(40):
            x = rng.choice([rng.uniform(10, 110), rng.uniform(W - 110, W - 10)]); yy = rng.uniform(0, H)
            d.ellipse([x - 10, yy - 6, x + 10, yy + 6], fill=(60, 140, 90))
        _cache["abyss"] = img
    return _cache["abyss"]

def drain_fn(T):
    q = clamp((T - OFF) / 0.5)
    if q >= 1: return abyss()
    return Image.blend(E.bg("sea").convert("RGBA"), abyss(), q)

def basin():
    """Mumbai seafront with the sea gone: sky, promenade, then an empty sloping valley."""
    if "basin" not in _cache:
        img = E.bg("ocean").convert("RGBA").copy(); d = ImageDraw.Draw(img)
        # city skyline
        rng = np.random.default_rng(11); x = 0
        while x < W:
            bw = int(rng.integers(70, 140)); top = int(rng.integers(900, 1100))
            d.rectangle([x, top, x + bw, 1230], fill=(150, 160, 190))
            for wy in range(top + 20, 1210, 50):
                for wx in range(x + 14, x + bw - 20, 34):
                    d.rectangle([wx, wy, wx + 16, wy + 24], fill=(220, 230, 250))
            x += bw + 10
        d.rectangle([0, 1230, W, 1275], fill=(170, 170, 176))
        for xx in range(0, W, 60): d.line([(xx, 1230), (xx, 1275)], fill=(140, 140, 150), width=3)
        # empty sea basin
        for i in range(8):
            y0 = 1275 + i * 85
            c = (int(150 - i * 14), int(120 - i * 11), int(90 - i * 8))
            d.rectangle([0, y0, W, y0 + 85], fill=c)
        for _ in range(30):
            xx, yy = rng.uniform(0, W), rng.uniform(1300, H)
            d.ellipse([xx - 14, yy - 6, xx + 14, yy + 6], fill=(70, 120, 80))
        _cache["basin"] = img
    return _cache["basin"]

# ---------------------------------------------------------------- props
def bubbles_props(frame, d, T, sc):
    for j in range(8):
        ph = (T * 0.5 + j / 8) % 1.0
        bx = 200 + j * 95 + 12 * math.sin(T * 3 + j); by = 1500 - 900 * ph; r = 7 + 10 * ph
        d.ellipse([bx - r, by - r, bx + r, by + r], outline=(220, 245, 255), width=4)
    top_label(frame, "~97% OF EARTH'S WATER")

def fish_fall(T):
    t = max(0.0, T - OFF - 0.3)
    return (540 + 30 * math.sin(T * 6), 1000 + 200 * clamp(t / 4) ** 2, 400)

def fish_rot(T):
    return 0 if T < OFF + 0.3 else 30 * math.sin((T - OFF) * 6)

def drained_props(frame, d, T, sc):
    if T > OFF + 0.5:
        top_label(frame, "SEAFLOOR: ~3.7 KM BELOW")
    # droplets falling with everything else
    for k in range(12):
        x = 160 + (k * 67) % 760; y = 500 + ((T - OFF) * 500 + k * 131) % 1100
        d.ellipse([x - 7, y - 10, x + 7, y + 10], fill=(150, 200, 240))

def whale_pos(T):
    t = T - 18.0
    return (500, 760 + 260 * clamp(t / 6) ** 1.5, 520)

def scale_props(frame, d, T, sc):
    # depth ruler on the right: 5-second fall vs the whole way down
    x = 880; y0, y1 = 520, 1300
    d.rectangle([x - 14, y0, x + 14, y1], fill=(40, 40, 60), outline=WHITE, width=4)
    fall = y0 + (y1 - y0) * (110 / 3700)
    d.rectangle([x - 14, y0, x + 14, fall + 6], fill=YEL)
    l1 = label("~100 M", 46, YEL); comp(frame, l1, x - l1.width - 30, fall - 26)
    l2 = label("3,700 M", 46, WHITE); comp(frame, l2, x - l2.width - 30, y1 - 50)
    top_label(frame, "5 SEC OF FALLING:")

def trench_props(frame, d, T, sc):
    lt = T - sc["s"]
    # V-shaped trench
    d.polygon([(0, 560), (300, 560), (540, 1340), (780, 560), (W, 560), (W, 1400), (0, 1400)], fill=(78, 58, 48))
    # Everest rising inside the trench
    p = ease_out(clamp((lt - 0.8) / 1.2))
    if p > 0:
        top = 1330 - 560 * p
        d.polygon([(400, 1330), (540, top), (680, 1330)], fill=(120, 110, 120), outline=OUTL)
        d.polygon([(540, top), (510, top + 90 * p), (540, top + 70 * p), (570, top + 90 * p)], fill=WHITE)
        if lt > 2.2:
            l = label("EVEREST 8.8 KM", 50, WHITE); comp(frame, l, 540 - l.width / 2, top - 80)
    top_label(frame, "CHALLENGER DEEP ~11 KM", 380)

def basin_props(frame, d, T, sc):
    top_label(frame, "MARINE DRIVE, MUMBAI", 380, WHITE)

def plankton_props(frame, d, T, sc):
    for k in range(26):
        x = 120 + (k * 97) % 840 + 14 * math.sin(T * 2 + k); y = 520 + (k * 61) % 700
        r = 8 + k % 3 * 4
        d.ellipse([x - r, y - r, x + r, y + r], fill=(110, 210, 120), outline=OUTL, width=3)
    top_label(frame, "~50% OF EARTH'S OXYGEN")

def back_overlay(frame, T, sc):
    q = clamp((T - BACK) / 0.45)
    if q >= 1: return frame
    blue = Image.new("RGBA", frame.size, (170, 220, 255, 255))
    return Image.blend(blue, frame, q)

def back_props(frame, d, T, sc):
    lt = T - sc["s"]
    for j in range(10):
        ph = (T * 0.6 + j / 10) % 1.0
        bx = 140 + j * 85; by = 1500 - 900 * ph; r = 6 + 9 * ph
        d.ellipse([bx - r, by - r, bx + r, by + r], outline=(220, 245, 255), width=4)
    if lt > 2.0:
        top_label(frame, "NOW ~100 M DEEPER")

def dizzy_after(frame, d, T, sc):
    for k in range(3):
        a = T * 4 + k * 2.1
        x = 540 + 120 * math.cos(a); y = 760 + 30 * math.sin(a)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=YEL, outline=OUTL, width=3)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="ocean", s=4.0, e=OFF, bg="sea", clock="OCEANS: ON", char="fish", pos=(540, 1000, 440),
         props=bubbles_props, look=(0.3, 0),
         narr="The ocean holds about 97% of all the water on Earth.", n_at=4.2,
         say="Just another day at the OFFICE.", say_at=6.6, pitch=640),
    dict(id="gone", s=OFF, e=18.0, bg_fn=drain_fn, clock="OCEANS OFF · 1 SEC", char="fish", pos=fish_fall,
         rot=fish_rot, props=drained_props, look=(0, 0.5),
         narr="POOF. The average seafloor is about 3.7 KM below the surface.", n_at=11.2,
         say="Where did my WATER go?!", say_at=13.6, pitch=660),
    dict(id="fall", s=18.0, e=25.0, bg_fn=lambda T: abyss(), clock="2 SEC", char="whale", pos=whale_pos,
         rot=lambda T: 8 * math.sin(T * 3), props=scale_props, look=(0, 0.5),
         narr="In 5 seconds, a falling whale drops only about 100 METRES.", n_at=18.2,
         say="I'm a WHALE, not a BIRD!", say_at=20.6, pitch=300),
    dict(id="trench", s=25.0, e=32.0, bg_fn=lambda T: abyss(), clock="3 SEC", props=trench_props,
         narr="The deepest spot is almost 11 KM down. Mount EVEREST would fit inside.", n_at=25.2),
    dict(id="mumbai", s=32.0, e=39.0, bg_fn=lambda T: basin(), clock="4 SEC", char="uncle", state="angry",
         pos=(540, 1010, 480), props=basin_props, look=(0, 0.5),
         narr="Mumbai's Marine Drive now overlooks a giant, empty VALLEY.", n_at=32.2,
         say="Who stole the ARABIAN SEA?!", say_at=34.6, pitch=220),
    dict(id="oxygen", s=39.0, e=BACK, bg_fn=lambda T: abyss(), clock="4.9 SEC", char="kid", pos=(540, 1060, 460),
         props=plankton_props, look=(0, -0.2),
         narr="Ocean plankton make roughly HALF of Earth's oxygen. Bring it BACK!", n_at=39.2,
         say="Ocean, PLEASE come back!", say_at=41.6, pitch=620),
    dict(id="twist", s=BACK, e=52.0, bg="sea", clock="5 SEC · OCEANS BACK", char="whale", pos=(540, 1060, 560),
         props=back_props, overlay=back_overlay, twist=True, look=(0.3, 0.2),
         narr="Water's back! Every falling fish is now about 100 METRES DEEPER.", n_at=45.4,
         say="Did anyone else feel THAT?", say_at=47.8, pitch=300),
    dict(id="outro", s=52.0, e=57.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("fish", 280, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540 + 200 * math.sin((T - 1.9) * 2), 1400, p)

cfg = dict(
    total=57.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("THE OCEANS", WHITE)], 140), 770, 0.75, "right"),
        (title([("VANISHED", WHITE)], 140), 915, 1.05, "left"),
        (title([("...for ", WHITE), ("5 SECONDS?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("see first?", YEL)], 110), 600, 0.45)],
               row=[("fish", 1), ("whale", 1), ("uncle", "angry"), ("kid", 1), ("earth", 0)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=OFF - 0.1, melody=True),
           dict(t0=52.0, t1=57.0, melody=True)],
    drones=[dict(t0=OFF, dur=BACK - OFF - 0.15, g=0.07)],
    fx=[("underwater", 4.0, 0.5, dict(dd=7.0)), ("powerdown", OFF + 0.05, 0.8), ("wind", OFF + 0.3, 0.4, dict(dd=6.0)),
        ("splash", BACK + 0.05, 1.2), ("waves", BACK + 0.1, 0.5, dict(dd=4.0)), ("bubbles", BACK + 0.4, 0.4, dict(dd=4.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_the_oceans_disappeared")
