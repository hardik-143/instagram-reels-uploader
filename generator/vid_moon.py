#!/usr/bin/env python3
"""What if you drove to the Moon? Cycle vs auto vs Vande Bharat vs rocket."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

EARTH = (170, 1250); MOON = (920, 1010)

def path(p):
    x = EARTH[0] + (MOON[0] - EARTH[0]) * p
    y = EARTH[1] + (MOON[1] - EARTH[1]) * p - 150 * math.sin(math.pi * p)
    return x, y

_earth_cache = {}
def route(frame, d, T, label=None):
    for i in range(1, 34):
        x, y = path(i / 34)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(150, 150, 190))
    comp(frame, draw_char("earth", 240, T, 0, False, (0.5, -0.2), T * 20), EARTH[0] - 120, EARTH[1] - 120)
    comp(frame, draw_char("moon", 220, T, 0, E.blink_at(T, 0.7), (-0.6, 0.2), 1), MOON[0] - 110, MOON[1] - 110)

@E.sfx
def bellring():
    s = E.ding(2400) * 0.5
    return s + np.concatenate([np.zeros(int(0.15 * E.SR)), s[:-int(0.15 * E.SR)]])

@E.sfx
def autohorn():
    t = E.tarr(0.5); s = np.sign(np.sin(2 * np.pi * 420 * t)) * 0.3 + np.sin(2 * np.pi * 840 * t) * 0.2
    s *= (np.sin(2 * np.pi * 8 * t) > -0.3)
    return E.lp(s, 3) * np.minimum(1, t / 0.01) * np.minimum(1, (0.5 - t) / 0.05) * 0.5

@E.sfx
def trainhorn():
    t = E.tarr(1.3); s = sum(np.sin(2 * np.pi * f * t) for f in (311, 370, 466)) / 3
    return s * np.minimum(1, t / 0.08) * np.minimum(1, (1.3 - t) / 0.2) * 0.4

@E.sfx
def launch(dd=3.0):
    t = E.tarr(dd); n = E.noise(len(t))
    return (E.lp(n, 30) * 3 + E.lp(n, 4) * 0.6) * np.minimum(1, t / 0.3) * np.minimum(1, (dd - t) / 0.6) * 0.45

def make_pos(sc_s, sc_e, p0, p1, B, dur=None):
    def pos(T):
        q = clamp((T - sc_s - 0.4) / ((dur or (sc_e - sc_s - 0.6))))
        x, y = path(p0 + (p1 - p0) * q)
        return (x, y - B * 0.35, B)
    return pos

def route_props(frame, d, T, sc):
    route(frame, d, T)

def cycle_after(frame, d, T, sc):
    x, y, B = sc["pos"](T)
    by = y + B * 0.42; sp = T * 8
    for wx in (x - 70, x + 70):
        d.ellipse([wx - 48, by - 48, wx + 48, by + 48], outline=(40, 40, 50), width=9)
        for k in range(4):
            a = sp + k * math.pi / 4
            d.line([(wx - 44 * math.cos(a), by - 44 * math.sin(a)), (wx + 44 * math.cos(a), by + 44 * math.sin(a))], fill=(120, 120, 130), width=3)
    d.line([(x - 70, by), (x, by - 50), (x + 70, by), (x - 10, by)], fill=(220, 50, 60), width=10, joint="curve")
    d.line([(x + 40, by - 70), (x + 70, by)], fill=(220, 50, 60), width=10)

def rocket_props(frame, d, T, sc):
    route(frame, d, T)
    x, y, B = sc["pos"](T)
    for i in range(12):
        q = clamp((T - sc["s"] - 0.4) / 1.6) - i * 0.015
        if q <= 0: continue
        tx, ty = path(min(1, q) * 1.0)
        r = 14 - i
        if r > 2: d.ellipse([tx - r, ty - r + B * 0.2, tx + r, ty + r + B * 0.2], fill=(255, 200 - i * 8, 80))

def twist_props(frame, d, T, sc):
    cx, cy = 540, 1080
    for k in range(3):
        rr = 330 + k * 40
        a0 = (T * 40 + k * 120) % 360
        d.arc([cx - rr, cy - rr * 0.6, cx + rr, cy + rr * 0.6], a0, a0 + 250, fill=(120, 200, 255), width=6)
    q = (T * 0.3) % 1.0
    a = 2 * math.pi * q * 3
    rx, ry = cx + 370 * math.cos(a), cy + 222 * math.sin(a)
    comp(frame, draw_char("rocket", 110, T, 0, False, (0, 0), 1).rotate(-math.degrees(a) - 90, resample=Image.BICUBIC, expand=True),
         rx - 70, ry - 70)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="dist", s=4.0, e=10.5, bg="space", clock="384,400 KM", char="moon", pos=(560, 1060, 560), look=(-0.4, 0.2),
         narr="The Moon is about 384,400 km away. Road trip?", n_at=4.2,
         say="Come visit! Bring SNACKS.", say_at=5.8, pitch=380),
    dict(id="cycle", s=10.5, e=17.0, bg="space", clock="CYCLE · 15 KM/H", char="kid", props=route_props,
         props_after=cycle_after, look=(0.6, -0.2),
         narr="By cycle at 15 km/h, nonstop: almost 3 YEARS.", n_at=10.7,
         say="My legs have LEFT the chat.", say_at=12.4, pitch=600),
    dict(id="auto", s=17.0, e=23.5, bg="space", clock="AUTO · 50 KM/H", char="auto", props=route_props,
         narr="By auto at 50 km/h: about 10 and a half MONTHS.", n_at=17.2,
         say="Meter se? That's a LOT of lakhs.", say_at=18.9, pitch=420),
    dict(id="train", s=23.5, e=30.0, bg="space", clock="VANDE BHARAT · 160 KM/H", char="train", props=route_props,
         narr="Vande Bharat at its top speed of 160 km/h: about 100 days.", n_at=23.7,
         say="Next station... the MOON.", say_at=25.6, pitch=300),
    dict(id="rocket", s=30.0, e=36.5, bg="space", clock="APOLLO 11", char="rocket", props=rocket_props,
         narr="Apollo 11 made it in about 3 DAYS.", n_at=30.2,
         say="3 days? Too EASY.", say_at=31.9, pitch=520),
    dict(id="chandrayaan", s=36.5, e=43.5, bg="space", clock="CHANDRAYAAN-3", char="moon", pos=(540, 1080, 520),
         props=twist_props, twist=True, look=(0, 0.2),
         narr="But Chandrayaan-3 took about 40 days... on PURPOSE.", n_at=36.7,
         say="Longer loops, less fuel. SMART.", say_at=38.8, pitch=380),
    dict(id="outro", s=43.5, e=48.5),
]
for sc, (p0, p1, B, dur) in {"cycle": (0.12, 0.20, 380, None), "auto": (0.14, 0.40, 380, None),
                             "train": (0.16, 0.66, 380, None), "rocket": (0.06, 0.96, 340, 1.6)}.items():
    scn = next(x for x in S if x["id"] == sc)
    scn["pos"] = make_pos(scn["s"], scn["e"], p0, p1, B, dur)

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 30 * math.sin(T * 3)
        paste_c(frame, draw_char("auto", 380, T, 0, False, (0, 0), 1), x, 1380, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=48.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU DROVE TO", WHITE)], 124), 770, 0.75, "right"),
        (title([("THE MOON?", WHITE)], 140), 915, 1.05, "left"),
        (title([("...in an ", WHITE), ("AUTO?", YEL)], 92), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which ride would ", WHITE), ("YOU", YEL)], 88), 470, 0.15),
                      (title([("take to the Moon?", YEL)], 100), 600, 0.45)],
               row=[("kid", 1), ("auto", 1), ("train", 1), ("rocket", 1), ("moon", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=36.35), dict(t0=43.5, t1=48.5, melody=True)],
    drones=[dict(t0=36.5, dur=7.0, g=0.08)],
    fx=[("autohorn", 2.0, 0.8), ("bellring", 10.9, 1.0), ("autohorn", 17.4, 1.0), ("autohorn", 21.5, 0.6),
        ("trainhorn", 23.8, 1.0), ("launch", 30.3, 1.0, dict(dd=3.0)), ("boom", 30.3, 0.6)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_drove_to_the_moon")
