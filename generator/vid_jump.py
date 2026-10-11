#!/usr/bin/env python3
"""What if all 1.46 billion Indians jumped at the same time?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

JUMP = 23.5      # everyone leaves the ground (scene "air" start)
AIR = 0.5        # time in the air for a ~30 cm jump (shown slowed down)
SLOW = 3.2       # slow-motion stretch for the jump on screen

def hop(T):
    """Height (0..1) of the slow-motion jump that starts at JUMP."""
    q = (T - JUMP - 0.3) / SLOW
    if q <= 0 or q >= 1: return 0.0
    return math.sin(math.pi * q)

# small crowd sprites (cached once, they only bob)
CROWD_KINDS = ["kid", "uncle", "kid", "uncle", "kid", "uncle", "kid"]
_crowd = {}
def crowd_spr(i):
    if i not in _crowd:
        _crowd[i] = draw_char(CROWD_KINDS[i % len(CROWD_KINDS)], 170, 0.0, 0, False, (0, 0.2), 1)
    return _crowd[i]

def crowd(frame, d, T, sc, jump=False, y0=1235):
    xs = [70, 210, 350, 730, 870, 1010]
    for i, x in enumerate(xs):
        h = hop(T + i * 0.05) * 160 if jump else 0
        bob = 6 * math.sin(T * 4 + i)
        spr = crowd_spr(i)
        comp(frame, spr, x - 85, y0 - 85 - h + bob)

def crowd_jump(frame, d, T, sc):
    crowd(frame, d, T, sc, jump=True)

def countdown(T):
    k = T - 17.0
    if k < 2.0: return "GET READY"
    if k < 3.0: return "3"
    if k < 4.0: return "2"
    if k < 5.0: return "1"
    return "JUMP!"

def kid_jump(T):
    return (540, 1080 - 330 * hop(T), 560)

def atom(frame, d, T, sc):
    cx, cy = 190, 1180
    for k in range(3):
        a = math.radians(k * 60 + T * 20)
        box = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.ellipse([20, 110, 280, 190], outline=(140, 200, 255), width=6)
        r = box.rotate(math.degrees(a), resample=Image.BICUBIC)
        comp(frame, r, cx - 150, cy - 150)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(250, 214, 10), outline=OUTL, width=4)
    for k in range(3):
        a = T * 2.5 + k * 2.1
        ex, ey = cx + 130 * math.cos(a), cy + 40 * math.sin(a)
        d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=(120, 220, 255))

def earth_nudge(T):
    p = 0.0
    if 37.5 <= T < 40.5: p = math.sin(math.pi * (T - 37.5) / 3.0)
    return (600, 1060 + 12 * p, 520)

def plaster(frame, d, T, sc):
    t = T - sc["s"]
    if t < 0.3: return
    for k in range(9):
        x = 100 + k * 110 + 20 * math.sin(k * 3)
        y = 360 + ((t - 0.3) * (260 + 40 * (k % 4)) + k * 30) % 900
        r = 6 + (k % 3) * 4
        d.rectangle([x - r, y - r, x + r, y + r], fill=(235, 228, 214), outline=OUTL, width=2)

def shake_living(T):
    base = E.bg("living")
    t = T - 49.5
    if t < 0 or t > 1.2: return base
    a = 14 * math.exp(-t * 3) * math.sin(t * 60)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); im.paste(base, (int(a), int(a * 0.5)))
    return im

@E.sfx
def stomp():
    t = E.tarr(1.6); n = E.noise(len(t))
    return (np.sin(2 * np.pi * 45 * t) * 0.9 + E.lp(n, 20) * 1.5) * np.exp(-t * 2.5) * 0.6

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="count", s=4.0, e=10.5, bg="gully", clock="1,460,000,000", char="kid", pos=(540, 1080, 560),
         props=crowd, look=(0.4, 0),
         narr="India has about 1.46 BILLION people. The most of any country.", n_at=4.2,
         say="That's a LOT of chappals.", say_at=6.2, pitch=600),
    dict(id="weight", s=10.5, e=17.0, bg="gully", clock="ROUGHLY 70 MILLION TONNES", char="uncle", pos=(540, 1080, 580),
         props=crowd, look=(-0.4, 0.1),
         narr="Together, we weigh roughly 70 MILLION tonnes.", n_at=10.7,
         say="Why is everyone looking at ME?", say_at=12.5, pitch=230),
    dict(id="ready", s=17.0, e=23.5, bg="gully", clock=countdown, char="kid", pos=(540, 1100, 560),
         props=crowd, look=(0, -0.3),
         narr="Same second, everyone, everywhere. 3... 2... 1...", n_at=17.2,
         say="Chappals OFF. Ready!", say_at=18.4, pitch=620),
    dict(id="air", s=23.5, e=30.0, bg="gully", clock="AIR TIME: 0.5 SEC", char="kid", pos=kid_jump,
         props=crowd_jump, look=(0, -0.5),
         narr="JUMP! A 30 cm jump keeps you up for about HALF a second.", n_at=23.6,
         say="I'm FLYING! Sort of.", say_at=27.0, pitch=640),
    dict(id="earth", s=30.0, e=36.5, bg="space", clock="EARTH VS. ALL OF US", char="earth", pos=(540, 1080, 560),
         look=(0, -0.3),
         narr="But Earth is about 80 TRILLION times heavier than all of us.", n_at=30.2,
         say="Was that... a TICKLE?", say_at=32.4, pitch=200),
    dict(id="push", s=36.5, e=43.0, bg="space", clock="EARTH MOVES...", char="earth", pos=earth_nudge,
         props=atom, look=(-0.5, 0.2),
         narr="Our push moves Earth about the width of an atom's NUCLEUS.", n_at=36.7,
         say="Ooh, I MOVED! Kind of.", say_at=38.8, pitch=200),
    dict(id="land", s=43.0, e=49.5, bg="gully", clock="LANDING", char="kid", pos=(540, 1080, 560),
         props=crowd, look=(0.3, 0.1),
         narr="Then we land, and Earth moves right BACK. Net change: zero.", n_at=43.2,
         say="That's IT?!", say_at=45.6, pitch=600),
    dict(id="twist", s=49.5, e=56.0, bg_fn=shake_living, clock="MEANWHILE...", char="uncle", state="angry",
         pos=(540, 1060, 560), props=plaster, twist=True, look=(0, -0.6),
         narr="Earth didn't notice. The uncle DOWNSTAIRS did.", n_at=49.8,
         say="Who is JUMPING up there?!", say_at=51.8, pitch=220),
    dict(id="outro", s=56.0, e=61.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        y = 1420 - 120 * abs(math.sin((T - 1.9) * 3.0))
        paste_c(frame, draw_char("kid", 340, T, 0, False, (0, -0.4), 1), 540, y, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=61.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("ALL 1.46 BILLION", WHITE)], 116), 770, 0.75, "right"),
        (title([("INDIANS", WHITE)], 150), 915, 1.05, "left"),
        (title([("JUMPED AT ", WHITE), ("ONCE?", YEL)], 100), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" jump?", WHITE)], 100), 470, 0.15),
                      (title([("Tell us below!", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("earth", 1), ("kid", 1), ("uncle", "angry")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=17.0), dict(t0=17.0, t1=23.4, drums=True, clap=False, minor=True),
           dict(t0=23.5, t1=49.35, melody=True), dict(t0=56.0, t1=61.0, melody=True)],
    drones=[dict(t0=30.0, dur=13.0, g=0.06)],
    fx=[("crowd", 4.2, 0.5, dict(dd=6.0)), ("tick", 19.0, 1.0), ("tick", 20.0, 1.0), ("tick", 21.0, 1.0),
        ("whoosh", JUMP + 0.2, 1.0), ("cheer", JUMP + 0.3, 0.9), ("boom", 43.2, 0.6),
        ("stomp", 49.6, 1.2), ("rumble", 49.6, 0.5, dict(dd=1.5))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_all_indians_jumped_at_once")
