#!/usr/bin/env python3
"""What if your speed doubled every 2 seconds? Walk at 5 km/h -> sound barrier -> escape Earth -> light?"""
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

def speed_lines(d, T, n=14, k=1.0, col=(255, 255, 255)):
    for i in range(n):
        y = 430 + (i * 71) % 900
        L = 120 + (i * 37) % 160
        x = W - ((T * 1400 * k + i * 263) % (W + L + 200))
        d.line([(x, y), (x + L, y)], fill=col, width=6)

def kph_label(text, frame, y=380, col=YEL):
    l = label(text, 60, col)
    comp(frame, l, 540 - l.width / 2, y)

# -------------------------------------------------------------- props
def walk_props(frame, d, T, sc):
    kph_label("x2 EVERY 2 SEC", frame)

def car_props(frame, d, T, sc):
    speed_lines(d, T, 10, 0.6)
    lt = T - sc["s"]
    # autos sliding backwards as you overtake them
    for k in range(2):
        x = 900 - ((lt * 260 + k * 520) % 1300)
        comp(frame, draw_char("auto", 230, T, 0, False, (0.6, 0), 1), x, 1060 + k * 40)

def train_props(frame, d, T, sc):
    speed_lines(d, T, 14, 1.0)
    lt = T - sc["s"]
    x = 780 - min(lt, 6) * 30
    comp(frame, draw_char("train", 260, T, 0, False, (-0.6, 0), 1), x, 1050)

def boom_props(frame, d, T, sc):
    speed_lines(d, T, 16, 1.6)
    lt = T - sc["s"]
    # sonic boom cone: rings trailing behind the kid
    for k in range(4):
        r = ((lt * 220 + k * 90) % 360) + 60
        a = int(255 * (1 - (r - 60) / 360))
        d.arc([340 - r, 1060 - r, 340 + r, 1060 + r], 120, 240, fill=(255, 255, 255, a), width=10)

def hot_props(frame, d, T, sc):
    speed_lines(d, T, 18, 2.2, (255, 220, 160))
    lt = T - sc["s"]
    glow = clamp(lt / 2.0)
    for k in range(6, 0, -1):
        r = 260 + k * 22
        c = (255, int(120 + 20 * k), 40)
        d.ellipse([560 - r * 0.6, 1060 - r * 0.85, 560 + r * 0.6, 1060 + r * 0.85],
                  outline=c, width=int(4 + 6 * glow))
    for k in range(10):
        x = 820 + ((T * 900 + k * 97) % 260); y = 900 + (k * 53) % 330
        rr = 10 + k % 3 * 6
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 160 + k * 8, 60))

def escape_props(frame, d, T, sc):
    lt = T - sc["s"]
    s = max(140, 420 - lt * 50)
    x0, y = 780 + lt * 10, 1120 + lt * 15
    comp(frame, draw_char("earth", int(s), T, 0, False, (-0.6, -0.4), T * 30), x0 - s / 2, y - s / 2)
    for k in range(8):
        x = 380 + (k - 3.5) * 30; yy = 1000 + ((lt * 500 + k * 41) % 260)
        d.line([(x, yy), (x, yy + 60)], fill=(255, 255, 255), width=4)

def moon_props(frame, d, T, sc):
    speed_lines(d, T, 16, 3.0)

def kid_fly_pos(T):
    sc = SC["moon"]; lt = T - sc["s"]
    return (180 + 40 * math.sin(T * 2), 1100, 260)

def moon_after(frame, d, T, sc):
    cx, cy, B = kid_fly_pos(T)
    comp(frame, draw_char("kid", B, T, 0, False, (1, 0), 1), cx - B / 2, cy - B / 2)

def moon_pos(T):
    lt = T - SC["moon"]["s"]
    return (700 - lt * 30, 1060, 460)

def light_props(frame, d, T, sc):
    lt = T - sc["s"]
    # stretched streaks of starlight
    for i in range(22):
        y = 380 + (i * 61) % 980
        L = 300 + (i * 53) % 400
        x = W - ((T * 2600 + i * 211) % (W + L + 300))
        d.line([(x, y), (x + L, y)], fill=(200, 220, 255), width=4)
    l = label("300,000 KM PER SEC", 58, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="walk", s=4.0, e=10.5, bg="gully", clock="0 SEC · 5 KM/H", char="kid", pos=(540, 1060, 520),
         props=walk_props, look=(0.4, 0),
         narr="You start walking at 5 km/h. Every 2 seconds, your speed DOUBLES.", n_at=4.2,
         say="Easy. I'm just WALKING.", say_at=6.6, pitch=600),
    dict(id="car", s=10.5, e=17.0, bg="speed", clock="8 SEC · 80 KM/H", char="kid", pos=(560, 900, 380),
         props=car_props, look=(0.7, 0), rot=-6,
         narr="8 seconds: 80 KM/H. You just overtook every auto on the road.", n_at=10.7,
         say="Bhaiya, SIDE do!", say_at=12.9, pitch=620, bubble_y=640),
    dict(id="train", s=17.0, e=23.5, bg="speed", clock="12 SEC · 320 KM/H", char="kid", pos=(500, 920, 380),
         props=train_props, look=(0.7, 0), rot=-10,
         narr="12 seconds: 320 KM/H. That's BULLET TRAIN top speed.", n_at=17.2,
         say="Train? I AM the train.", say_at=19.4, pitch=620, bubble_y=660),
    dict(id="boom", s=23.5, e=30.0, bg="speed", clock="16 SEC · 1,280 KM/H", char="kid", pos=(560, 1060, 420),
         props=boom_props, look=(0.7, 0), rot=-14,
         narr="16 seconds: faster than SOUND. A sonic BOOM follows you everywhere.", n_at=23.7,
         say="Who burst a CRACKER?!", say_at=26.0, pitch=620),
    dict(id="hot", s=30.0, e=36.5, bg="hot", clock="20 SEC · 5,120 KM/H", char="kid", pos=(560, 1060, 420),
         props=hot_props, look=(0.7, 0), rot=-18, state="puff",
         narr="20 seconds: the air squeezed in front of you turns RED HOT.", n_at=30.2,
         say="I'm a METEOR now!", say_at=32.6, pitch=640),
    dict(id="escape", s=36.5, e=43.0, bg="space", clock="26 SEC · 40,960 KM/H", char="kid", pos=(380, 880, 300),
         props=escape_props, look=(0.3, -0.6),
         narr="26 seconds: past 40,000 KM/H. Fast enough to ESCAPE Earth's gravity.", n_at=36.7,
         say="Bye bye, EARTH!", say_at=39.0, pitch=640, bubble_y=640),
    dict(id="moon", s=43.0, e=49.5, bg="space", clock="53 SEC · MOON", char="moon", pos=moon_pos,
         props=moon_props, props_after=moon_after, look=(-0.6, 0),
         narr="About 53 seconds: you zip past the MOON. Apollo 11 took 3 DAYS.", n_at=43.2,
         say="Arre, slow DOWN!", say_at=45.6, pitch=380),
    dict(id="light", s=49.5, e=57.5, bg="space", clock="55 SEC · LIGHT SPEED?", char="kid", pos=(540, 1060, 460),
         props=light_props, twist=True, look=(0, 0.2),
         narr="Speed of LIGHT at 55 seconds? Physics says NO. Nothing with mass can reach it.", n_at=49.7,
         say="Universe has a SPEED LIMIT?!", say_at=52.4, pitch=600),
    dict(id="outro", s=57.5, e=62.5),
]
SC = {s["id"]: s for s in S}

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        x = 540 + 280 * math.sin((T - 1.9) * 2.5)
        paste_c(frame, draw_char("kid", 300, T, 0, False, (1, 0), 1), x, 1400, p)

cfg = dict(
    total=62.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOUR SPEED", WHITE)], 140), 770, 0.75, "right"),
        (title([("DOUBLED", WHITE)], 150), 915, 1.05, "left"),
        (title([("...every ", WHITE), ("2 SECONDS?", YEL)], 92), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("At what second would", WHITE)], 80), 470, 0.15),
                      (title([("YOU", YEL), (" hit the brakes?", WHITE)], 92), 600, 0.45)],
               row=[("kid", 1), ("auto", 1), ("train", 1), ("earth", 1), ("moon", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=49.35), dict(t0=57.5, t1=62.5, melody=True)],
    drones=[dict(t0=49.5, dur=8.0, g=0.08)],
    fx=[("whoosh", 11.0, 0.8), ("whoosh", 17.4, 1.0), ("boom", 24.0, 1.2), ("boom", 26.2, 0.6),
        ("wind", 30.2, 0.5, dict(dd=6.0)), ("rumble", 36.7, 0.5, dict(dd=4.0)), ("whoosh", 43.6, 1.0)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_your_speed_doubled")
