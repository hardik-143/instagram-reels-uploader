#!/usr/bin/env python3
"""What if you counted to 1 billion, out loud, one number a second?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_num = {}
def num_spr(txt, size=120):
    k = (txt, size)
    if k not in _num: _num[k] = text_sprite([(txt, YEL)], size, stroke=10)
    return _num[k]

def counter(T):
    return f"COUNT: {int(T - 4.0) + 1}"

def floating_numbers(frame, d, T, sc):
    for k in range(6):
        ph = (T * 0.35 + k / 6) % 1.0
        x = (110 if k % 2 == 0 else 880) + 40 * math.sin(T + k)
        y = 1240 - 360 * ph
        if 880 < y < 1240:
            spr = num_spr(str((k * 37 + int(T)) % 100 + 1), 70)
            comp(frame, spr, x - spr.width / 2, y)

def calendar(frame, d, T, sc, pages=4):
    # a desk calendar whose pages flip
    cx, cy = 840, 1230
    d.rounded_rectangle([cx - 110, cy - 120, cx + 110, cy + 110], radius=16, fill=WHITE, outline=OUTL, width=6)
    d.rectangle([cx - 110, cy - 120, cx + 110, cy - 70], fill=(225, 50, 60), outline=OUTL, width=6)
    day = int((T - sc["s"]) * pages) % 31 + 1
    spr = num_spr(str(day), 90)
    comp(frame, spr, cx - spr.width / 2, cy - 60)

def cal_fast(frame, d, T, sc):
    calendar(frame, d, T, sc, pages=6)

def chai_props(frame, d, T, sc):
    cx, cy = 840, 1180   # a kulhad of chai, just out of reach
    d.polygon([(cx - 80, cy - 70), (cx + 80, cy - 70), (cx + 55, cy + 80), (cx - 55, cy + 80)],
              fill=(196, 104, 62), outline=OUTL, width=6)
    d.ellipse([cx - 80, cy - 90, cx + 80, cy - 50], fill=(214, 160, 110), outline=OUTL, width=6)
    for k in range(3):
        x0 = cx - 40 + k * 40
        pts = [(x0 + 12 * math.sin(T * 3 + j * 0.7 + k), cy - 110 - j * 18) for j in range(7)]
        d.line(pts, fill=(255, 255, 255), width=6, joint="curve")

def flakes(frame, d, T, sc):
    for k in range(28):
        x = (k * 97 + 40 * math.sin(T + k)) % W
        y = (k * 173 + T * (70 + k % 5 * 15)) % H
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 255))

def crowd_props(frame, d, T, sc):
    for i, x in enumerate([90, 230, 850, 990]):
        spr = draw_char("kid" if i % 2 else "uncle", 170, T, 0, False, (0, 0.2), 1)
        comp(frame, spr, x - 85, 1235 - 85 + 6 * math.sin(T * 4 + i))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="rule", s=4.0, e=11.0, bg="living", clock=counter, char="kid", pos=(540, 1080, 560),
         props=floating_numbers, look=(0, -0.3),
         narr="One number every second. No sleep, no breaks, no chai.", n_at=4.2,
         say="One... two... THREE...", say_at=6.2, pitch=600),
    dict(id="lakh", s=11.0, e=18.0, bg="night", clock="1 LAKH", char="kid", pos=(460, 1090, 540),
         props=calendar, look=(0.5, 0.1),
         narr="Reaching 1 LAKH takes about 28 HOURS. More than a day.", n_at=11.2,
         say="My throat is SO dry.", say_at=13.8, pitch=580),
    dict(id="million", s=18.0, e=25.0, bg="bedroom", clock="1 MILLION", char="kid", pos=(440, 1090, 540),
         props=chai_props, look=(0.6, 0.2),
         narr="1 MILLION takes about 11 and a half DAYS.", n_at=18.2,
         say="Not even ONE chai break?", say_at=20.6, pitch=600),
    dict(id="crore", s=25.0, e=32.0, bg="diwali", clock="1 CRORE", char="kid", pos=(460, 1090, 540),
         props=cal_fast, look=(0.4, -0.2),
         narr="1 CRORE takes about 116 days. Almost 4 MONTHS.", n_at=25.2,
         say="Wait, I MISSED Diwali?!", say_at=27.6, pitch=600),
    dict(id="billion", s=32.0, e=39.0, bg="living", clock="1 BILLION", char="uncle", pos=(540, 1080, 580),
         props=floating_numbers, look=(0, -0.2),
         narr="1 BILLION takes almost 32 YEARS of nonstop counting.", n_at=32.2,
         say="I started this as a KID!", say_at=34.6, pitch=230),
    dict(id="india", s=39.0, e=46.0, bg="gully", clock="1.46 BILLION", char="uncle", state="angry",
         pos=(540, 1080, 560), props=crowd_props, look=(0.3, 0),
         narr="One number for every Indian, 1.46 BILLION: over 46 YEARS.", n_at=39.2,
         say="Did anyone count ME?", say_at=42.0, pitch=220),
    dict(id="trillion", s=46.0, e=53.0, bg="pole", clock="1 TRILLION", char="earth", pos=(540, 1080, 520),
         props=flakes, look=(0, -0.2),
         narr="1 TRILLION takes about 31,700 years. Back then: the ICE AGE.", n_at=46.2,
         say="Brr! I REMEMBER that.", say_at=49.0, pitch=200),
    dict(id="twist", s=53.0, e=60.0, bg="living", clock="THE CATCH", char="kid", pos=(540, 1080, 560),
         twist=True, look=(0, -0.4),
         narr="The catch? Big numbers take SECONDS to say. The real count: way LONGER.", n_at=53.2,
         say="Ninety-nine crore, ninety-nine lakh... WHERE was I?", say_at=56.4, pitch=600),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        paste_c(frame, draw_char("kid", 340, T, 0.5 + 0.5 * math.sin(T * 20), False, (0, -0.3), 1), 540, 1400,
                ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU COUNTED", WHITE)], 128), 770, 0.75, "right"),
        (title([("TO 1 BILLION?", WHITE)], 128), 910, 1.05, "left"),
        (title([("...out ", WHITE), ("LOUD?", YEL)], 96), 1055, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("How far could ", WHITE), ("YOU", YEL)], 92), 470, 0.15),
                      (title([("count?", YEL)], 120), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("uncle", "angry"), ("earth", 1), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0), dict(t0=32.0, t1=52.85, melody=True),
           dict(t0=60.0, t1=65.0, melody=True)],
    fx=[("tick", 5.0, 0.8), ("tick", 6.0, 0.8), ("tick", 7.0, 0.8), ("tick", 8.0, 0.8), ("tick", 9.0, 0.8),
        ("tick", 10.0, 0.8), ("click", 11.4, 0.6), ("click", 25.4, 0.6), ("crowd", 39.2, 0.5, dict(dd=6.0)),
        ("wind", 46.0, 0.6, dict(dd=7.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_counted_to_a_billion")
