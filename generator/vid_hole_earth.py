#!/usr/bin/env python3
"""What if you dug a hole through the Earth from India? Kola borehole -> 38-minute fall -> Pacific Ocean."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

# ---------------------------------------------------------------- Earth cross-section with a tunnel
CX, CY, R = 540, 1040, 290
LAYERS = [(1.00, (120, 84, 60)), (0.97, (226, 104, 46)), (0.55, (250, 170, 50)), (0.19, (255, 236, 150))]
NAMES = [("CRUST", 0.985), ("MANTLE", 0.76), ("OUTER CORE", 0.37), ("INNER CORE", 0.0)]

def cross_section(d, frame, T, names=False, glow=0.0):
    for f, col in LAYERS:
        r = R * f
        d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=col, outline=OUTL, width=5)
    if glow > 0:
        for k in range(4):
            r = R * 0.19 + 10 + k * 14 + 6 * math.sin(T * 6 + k)
            d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=(255, 250, 220), width=int(3 + 3 * glow))
    # tunnel
    d.rectangle([CX - 16, CY - R - 4, CX + 16, CY + R + 4], fill=(30, 22, 30))
    if names:
        for n, f in NAMES[1:3]:
            l = label(n, 36, WHITE)
            comp(frame, l, CX + 40, CY - R * f - l.height / 2 - 10)

def faller(frame, T, p, B=110):
    """p: 0 = top of tunnel, 1 = bottom"""
    y = CY - R + 2 * R * p
    spr = draw_char("kid", B, T, 0, False, (0, 0.6 if p < 0.5 else -0.6), 1)
    comp(frame, spr, CX - B / 2, y - B / 2)

def fall_p(t):
    # simple-harmonic fall: position along tunnel for t in [0, 1] of the one-way trip
    return (1 - math.cos(math.pi * clamp(t))) / 2

# ---------------------------------------------------------------- props
def kola_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a thin borehole going down, drawn to the bottom of the screen
    q = clamp(lt / 3.0)
    d.rectangle([760, 1040, 790, 1040 + 260 * q], fill=(40, 30, 30))
    l = label("12.3 KM DEEP", 60, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

def scale_props(frame, d, T, sc):
    l = label("KOLA = 0.1% OF THE WAY", 58, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

def jump_props(frame, d, T, sc):
    cross_section(d, frame, T, names=True)
    lt = T - sc["s"]
    faller(frame, T, 0.42 * clamp((lt - 0.8) / 5.5) ** 2)

def centre_props(frame, d, T, sc):
    cross_section(d, frame, T)
    lt = T - sc["s"]
    faller(frame, T, 0.42 + 0.08 * clamp(lt / 1.5))

def hot_props(frame, d, T, sc):
    cross_section(d, frame, T, glow=clamp((T - sc["s"]) / 1.5))
    lt = T - sc["s"]
    faller(frame, T, 0.5 + 0.05 * clamp(lt / 6))

def slow_props(frame, d, T, sc):
    cross_section(d, frame, T)
    lt = T - sc["s"]
    faller(frame, T, 0.56 + 0.38 * ease_out(clamp(lt / 5.0)))

def splash_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(10):
        a = math.pi * (0.1 + 0.8 * k / 9)
        r = 60 + 260 * clamp(lt / 1.2)
        x = 300 + r * math.cos(a); y = 1260 - r * math.sin(a) * 0.9
        if lt < 2.5:
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(220, 240, 255), outline=(40, 120, 200), width=4)
    l = label("PACIFIC OCEAN", 62, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

def kid_pop_after(frame, d, T, sc):
    lt = T - sc["s"]
    y = 1240 - 160 * ease_back(clamp(lt / 0.6))
    comp(frame, draw_char("kid", 220, T, 0, False, (0.6, 0), "puff"), 300 - 110, y - 110)
    # water line in front of the kid
    d.rectangle([0, 1250, W, 1300], fill=(40, 120, 200))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="kola", s=4.0, e=11.0, bg="digsite", clock="KOLA, RUSSIA", char="uncle", state="hat",
         pos=(540, 1060, 500), props=kola_props, look=(0.4, 0.3),
         narr="The deepest hole ever drilled is about 12 KM. It took 19 YEARS.", n_at=4.2,
         say="19 years for THIS?", say_at=6.8, pitch=220),
    dict(id="scale", s=11.0, e=17.5, bg="space", clock="12,742 KM", char="earth", pos=(540, 1060, 520),
         props=scale_props, look=(0, 0.2),
         narr="But Earth is 12,742 KM thick. That hole barely scratched me.", n_at=11.2,
         say="Tickles, BAS.", say_at=13.6, pitch=360),
    dict(id="jump", s=17.5, e=24.5, bg="space", clock="0 MIN · JUMP!", props=jump_props,
         narr="Say we dig a heat-proof tunnel from INDIA and you JUMP in.", n_at=17.7,
         say="Wheeeeee!", say_at=19.6, pitch=640, bubble_y=600, narr_y=1500),
    dict(id="centre", s=24.5, e=31.0, bg="space", clock="19 MIN · CENTRE", props=centre_props,
         narr="Gravity speeds you up. At the centre: over 28,000 KM/H.", n_at=24.7,
         say="NO BRAKES, mummy!", say_at=27.0, pitch=640, bubble_y=600, narr_y=1500),
    dict(id="hot", s=31.0, e=37.5, bg="space", clock="5,200°C", props=hot_props,
         narr="The inner core is about 5,200°C. The Sun's surface: about 5,500°C.", n_at=31.2,
         say="Good thing the tunnel is HEAT-PROOF!", say_at=33.6, pitch=640, bubble_y=600, narr_y=1500),
    dict(id="slow", s=37.5, e=44.0, bg="space", clock="38 MIN", props=slow_props,
         narr="Then you slow down... and reach the other side in about 38 MINUTES.", n_at=37.7,
         say="Faster than my OFFICE commute!", say_at=40.4, pitch=640, bubble_y=600, narr_y=1500),
    dict(id="pacific", s=44.0, e=51.5, bg="ocean", clock="THE OTHER SIDE", char="fish", pos=(760, 1080, 300),
         props=splash_props, props_after=kid_pop_after, twist=True, look=(-0.6, 0),
         narr="But the other side of India is... the PACIFIC OCEAN, off South America.", n_at=44.2,
         say="Welcome! Bring a TOWEL?", say_at=47.0, pitch=480),
    dict(id="outro", s=51.5, e=56.5),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        paste_c(frame, draw_char("earth", 320, T, 0, False, (0, 0), T * 20), 540, 1420, p)

cfg = dict(
    total=56.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU DUG A HOLE", WHITE)], 116), 770, 0.75, "right"),
        (title([("THROUGH EARTH", WHITE)], 116), 915, 1.05, "left"),
        (title([("...from ", WHITE), ("INDIA?", YEL)], 100), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" jump in?", WHITE)], 96), 470, 0.15),
                      (title([("Yes or no?", YEL)], 110), 600, 0.45)],
               row=[("uncle", "hat"), ("earth", 1), ("kid", 1), ("sun", 1), ("fish", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=43.85), dict(t0=51.5, t1=56.5, melody=True)],
    drones=[dict(t0=31.0, dur=6.5, g=0.06)],
    fx=[("rumble", 4.3, 0.4, dict(dd=3.0)), ("whoosh", 18.6, 1.0), ("wind", 19.0, 0.5, dict(dd=12.0)),
        ("splash", 44.3, 1.0), ("waves", 44.5, 0.4, dict(dd=6.0)), ("seagulls", 46.0, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_dug_through_earth")
