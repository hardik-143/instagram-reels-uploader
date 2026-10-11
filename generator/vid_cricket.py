#!/usr/bin/env python3
"""What if cricket had never come to India?"""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

IMPACT = 28.6

def intro_extra(frame, d, T):
    if T < 1.9: return
    if T < 3.2:
        s = ease_back((T - 1.9) / 0.4)
    else:
        s = max(0.0, 1 - (T - 3.2) / 0.25)
    if s > 0.02:
        spr = draw_char("bat", 380, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540, 1390, s)
    if 3.2 <= T < 3.9:  # poof
        p = (T - 3.2) / 0.7
        for i in range(8):
            a = i * math.pi / 4
            r = 40 + 160 * ease_out(p); rr = 46 * (1 - p)
            x, y = 540 + r * math.cos(a), 1390 + r * math.sin(a)
            if rr > 1: d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(220, 210, 240))

def gully_props(frame, d, T, sc):
    pass

def gully_after(frame, d, T, sc):
    wx, wy = 890, 970
    if T < IMPACT and T >= IMPACT - 0.45:
        p = (T - (IMPACT - 0.45)) / 0.45
        x = 600 + (wx - 600) * p; y = 1300 + (wy - 1300) * p - 180 * math.sin(math.pi * p)
        spr = draw_char("football", 110, T, 0, False, (0, 0), 1).rotate(-p * 540, resample=Image.BICUBIC)
        comp(frame, spr, x - 55, y - 55)
    if T >= IMPACT:
        for a in range(0, 360, 40):
            r = 70 + (a % 80)
            d.line([(wx, wy), (wx + r * math.cos(math.radians(a)), wy + 0.8 * r * math.sin(math.radians(a)))],
                   fill=(250, 250, 255), width=5)
        d.ellipse([wx - 14, wy - 14, wx + 14, wy + 14], fill=(250, 250, 255))
        v = T - IMPACT
        if v < 0.9:
            x = wx - 200 * v; y = wy + 900 * v * v - 100 * v
            comp(frame, draw_char("football", 110, T, 0, False, (0, 0), 1).rotate(v * 400, resample=Image.BICUBIC), x - 55, y - 55)

def living_props(frame, d, T, sc):
    g = 150 + int(40 * math.sin(T * 9) * math.sin(T * 2.3))
    d.rounded_rectangle([758, 898, 1042, 1092], radius=6, fill=(90, g, 100))
    d.line([(760, 1040), (1040, 1040)], fill=WHITE, width=3)
    bx = 900 + 120 * math.sin(T * 1.7)
    d.ellipse([bx - 9, 960, bx + 9, 978], fill=WHITE)

def uncle_state(T):
    return "angry" if T >= 33.6 else 1

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="ship", s=4.0, e=11.0, bg="sea1721", clock="1721 · GUJARAT", char="bat", pos=(540, 1090, 560),
         narr="India's first recorded cricket? Gujarat, 1721. English sailors played it.", n_at=4.3,
         say="Plot twist: I never got off the SHIP.", say_at=6.8, pitch=380),
    dict(id="hockey", s=11.0, e=18.0, bg="stadium", clock="1928 – 1980", char="hockey", pos=(540, 1080, 580),
         narr="Hockey stays No. 1. India won 8 Olympic golds in it.", n_at=11.2,
         say="Finally, people remember my NAME.", say_at=12.9, pitch=460),
    dict(id="football", s=18.0, e=25.0, bg="stadium", clock="1950", char="football", pos=(540, 1080, 580),
         narr="India qualified for the 1950 FIFA World Cup... then withdrew.", n_at=18.2,
         say="Without cricket? We'd have SHOWN UP.", say_at=20.1, pitch=520),
    dict(id="gully", s=25.0, e=32.0, bg="gully", clock="SUNDAY 4 PM", char="kid", pos=(540, 1100, 560),
         look=(0.6, -0.2), narr="Gully cricket becomes gully FOOTBALL.", n_at=25.2,
         say="Broken windows? Still GUARANTEED.", say_at=26.3, pitch=600, props_after=gully_after),
    dict(id="tv", s=32.0, e=39.0, bg="living", clock="EVERY MATCH DAY", char="uncle", pos=(380, 1080, 560),
         look=(0.9, 0.1), state=uncle_state, twist=True, props=living_props,
         narr="But one thing would NEVER change...", n_at=32.2,
         say="REFEREE! Even I could do BETTER!", say_at=34.0, pitch=230),
    dict(id="outro", s=39.0, e=44.0),
]

cfg = dict(
    total=44.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("CRICKET", WHITE)], 140), 770, 0.75, "right"),
        (title([("NEVER CAME", WHITE)], 130), 915, 1.05, "left"),
        (title([("...to ", WHITE), ("INDIA?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which sport would India", WHITE)], 80), 470, 0.15),
                      (title([("be ", YEL), ("CRAZY", WHITE), (" about?", YEL)], 108), 600, 0.45)],
               row=[("bat", 1), ("hockey", 1), ("football", 1), ("kid", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=31.85), dict(t0=39.0, t1=44.0, melody=True)],
    drones=[],
    fx=[("whoosh", 3.2, 0.8), ("pop", 3.25, 1.0),
        ("waves", 4.0, 0.7, dict(dd=7.0)), ("seagulls", 4.6, 1.0),
        ("crowd", 11.0, 0.6, dict(dd=14.0)), ("cheer", 11.3, 0.8), ("whistle", 18.3, 1.0), ("cheer", 18.4, 0.5),
        ("whoosh", IMPACT - 0.45, 0.6, dict(dd=0.4)), ("crash", IMPACT, 1.1),
        ("crowd", 32.2, 0.35, dict(dd=6.8)), ("whistle", 33.5, 0.7)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_cricket_never_came_to_india")
