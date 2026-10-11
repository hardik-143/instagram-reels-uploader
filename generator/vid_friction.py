#!/usr/bin/env python3
"""What if friction disappeared for 5 seconds?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

OFF = 10.5     # friction switches off
BACK = 43.0    # friction returns (twist)

def sprite(w, h, draw):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); draw(ImageDraw.Draw(im), w, h); return im

def _shoe(d, w, h):
    d.rounded_rectangle([4, h * 0.3, w - 4, h - 6], radius=20, fill=(230, 80, 70), outline=OUTL, width=6)
    d.rectangle([4, h - 26, w - 4, h - 6], fill=WHITE, outline=OUTL, width=5)
    for x in range(int(w * 0.3), int(w * 0.7), 18): d.line([(x, h * 0.35), (x + 12, h * 0.5)], fill=WHITE, width=4)
def _chappal(d, w, h):
    d.rounded_rectangle([4, h * 0.45, w - 4, h - 4], radius=24, fill=(70, 120, 200), outline=OUTL, width=5)
    d.line([(w * 0.25, h * 0.5), (w * 0.4, h * 0.15), (w * 0.55, h * 0.5)], fill=(250, 214, 10), width=8)
def _box(d, w, h):
    d.rectangle([4, 4, w - 4, h - 4], fill=(200, 150, 90), outline=OUTL, width=5)
    d.line([(4, h * 0.35), (w - 4, h * 0.35)], fill=OUTL, width=4)
def _screw(d, w, h):
    d.ellipse([4, 4, w - 4, 34], fill=(180, 180, 190), outline=OUTL, width=4)
    d.line([(w / 2 - 10, 19), (w / 2 + 10, 19)], fill=OUTL, width=4)
    d.polygon([(w / 2 - 9, 32), (w / 2 + 9, 32), (w / 2, h - 4)], fill=(180, 180, 190), outline=OUTL)
    for y in range(42, h - 14, 12): d.line([(w / 2 - 8, y), (w / 2 + 8, y + 5)], fill=OUTL, width=3)

SHOE = sprite(150, 90, _shoe); CHAPPAL = sprite(140, 70, _chappal); BOX = sprite(110, 90, _box); SCREW = sprite(50, 120, _screw)

def ice_road(frame, d, T, sc):
    # shiny streaks on the road to show "no grip"
    for k in range(6):
        x = (k * 210 + T * 60) % 1300 - 110
        d.line([(x, 1400 + k * 18), (x + 160, 1390 + k * 18)], fill=(210, 230, 250), width=6)

def kid_slip(T):
    t = T - OFF
    return (540 + 30 * math.sin(t * 9), 950, 460)

def kid_rot(T):
    return 9 * math.sin((T - OFF) * 9)

def legs(frame, d, T, sc):
    # cartoon legs spinning in place under the kid
    x, y, B = val_pos(sc, T)
    for k in (-1, 1):
        a = (T * 14) + (0 if k < 0 else math.pi)
        fx = x + k * 50 + 70 * math.sin(a); fy = y + B * 0.62 + 25 * math.cos(a)
        d.line([(x + k * 40, y + B * 0.40), (fx, fy)], fill=(60, 90, 160), width=26)
        spr = SHOE
        comp(frame, spr, fx - 75, fy - 30)
    ice_road(frame, d, T, sc)

def val_pos(sc, T):
    p = sc["pos"]; return p(T) if callable(p) else p

def auto_pos(T):
    t = T - 17.0
    return (180 + 100 * t, 1150, 520)

def auto_rot(T):
    return 6 * math.sin((T - 17.0) * 5)

def table(frame, d, T, sc):
    t = T - sc["s"]
    tx = 30 * math.sin(t * 2.0)
    d.rectangle([150 + tx, 1240, 930 + tx, 1270], fill=(150, 100, 60), outline=OUTL, width=5)
    for lx in (200, 860):
        lean = 18 * math.sin(t * 1.7 + lx)
        d.line([(lx + tx, 1270), (lx + tx + lean, 1450)], fill=(120, 80, 50), width=22)
    for i, (sx, sy) in enumerate([(240, 520), (840, 600), (160, 900), (930, 880)]):
        spr = SCREW.rotate(t * 70 * (1 if i % 2 else -1), resample=Image.BICUBIC, expand=True)
        comp(frame, spr, sx + 20 * t * (1 if i % 2 else -1) - spr.width / 2, sy - 30 * t - spr.height / 2)

def chai_pos(T):
    t = T - 23.5
    return (300 + 80 * t, 1110, 440)

def laces(frame, d, T, sc):
    t = T - sc["s"]
    for i, (sx, sy, sp) in enumerate([(400, 1270, -1), (680, 1270, 1)]):
        x = sx + sp * 25 * t; y = sy
        comp(frame, SHOE, x - 75, y - 45)
        for k in range(2):
            ang = t * 3 + k * 2 + i
            ex = x + sp * (60 + 50 * k) * (0.4 + 0.6 * clamp(t / 2)); ey = y - 40 - 50 * math.sin(ang) * clamp(t / 2)
            d.line([(x, y - 40), ((x + ex) / 2, ey - 30), (ex, ey)], fill=WHITE, width=8, joint="curve")

def ball_pos(T):
    t = T - 36.5
    x = 200 + (t * 210) % 760
    return (x, 1150, 380)

def ball_rot(T):
    return -(T - 36.5) * 200

def pile(frame, d, T, sc):
    q = clamp((T - BACK - 0.25) / 0.5)
    items = [(SHOE, 130, 1250, 30), (CHAPPAL, 270, 1290, -15), (BOX, 840, 1200, 10), (CHAPPAL, 950, 1280, 160),
             (SHOE, 820, 1290, -40), (BOX, 160, 1150, 5)]
    for i, (spr, fx, fy, rot) in enumerate(items):
        sx = -200 if i % 2 == 0 else 1280
        x = sx + (fx - sx) * ease_out(q)
        r = spr.rotate(rot * q, resample=Image.BICUBIC, expand=True)
        comp(frame, r, x - r.width / 2, fy - r.height / 2)

def stadium_props(frame, d, T, sc):
    for k in range(5):
        x = (k * 260 - (T - 36.5) * 260) % 1300 - 110
        d.line([(x, 1290), (x + 120, 1290)], fill=WHITE, width=6)

@E.sfx
def slide(dd=3.0):
    t = E.tarr(dd); n = E.noise(len(t))
    return E.lp(n, 6) * np.sin(np.pi * t / dd) * 0.5

@E.sfx
def autohorn():
    t = E.tarr(0.5); s = np.sign(np.sin(2 * np.pi * 420 * t)) * 0.3 + np.sin(2 * np.pi * 840 * t) * 0.2
    s *= (np.sin(2 * np.pi * 8 * t) > -0.3)
    return E.lp(s, 3) * np.minimum(1, t / 0.01) * np.minimum(1, (0.5 - t) / 0.05) * 0.5

@E.sfx
def sproing():
    t = E.tarr(0.6); f = 300 + 500 * np.exp(-t * 6) * np.cos(2 * np.pi * 12 * t)
    return np.sin(E.osc(f)) * np.exp(-t * 4) * 0.4

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="grip", s=4.0, e=10.5, bg="gully", clock="FRICTION: ON", char="kid", pos=(540, 1080, 560), look=(0.4, 0),
         narr="Friction is the invisible GRIP between any two surfaces.", n_at=4.2,
         say="Never heard of her.", say_at=6.4, pitch=600),
    dict(id="walk", s=OFF, e=17.0, bg="gully", clock="FRICTION OFF · 1 SEC", char="kid", pos=kid_slip, rot=kid_rot,
         props=legs, look=(0, 0.4),
         narr="Walking means pushing the ground BACK. No friction, no push.", n_at=10.7,
         say="Legs moving. Me? NOT.", say_at=12.8, pitch=620),
    dict(id="auto", s=17.0, e=23.5, bg="gully", clock="2 SEC", char="auto", pos=auto_pos, rot=auto_rot,
         props=ice_road,
         narr="Tyres grip the road with friction. Now: no BRAKES, no turning.", n_at=17.2,
         say="Brake? Which BRAKE?!", say_at=19.2, pitch=420),
    dict(id="chai", s=23.5, e=30.0, bg="living", clock="3 SEC", char="chai", pos=chai_pos, props=table,
         narr="Nails and screws hold on with friction too. Furniture starts LOOSENING.", n_at=23.7,
         say="Bye bye, TABLE!", say_at=25.8, pitch=520),
    dict(id="laces", s=30.0, e=36.5, bg="gully", clock="4 SEC", char="kid", pos=(540, 990, 480), props=laces,
         look=(0, 0.6),
         narr="Knots need friction to hold. Every shoelace slips UNDONE.", n_at=30.2,
         say="Mine were never tied ANYWAY.", say_at=32.2, pitch=600),
    dict(id="ball", s=36.5, e=BACK, bg="stadium", clock="4.9 SEC", char="football", pos=ball_pos, rot=ball_rot,
         props=stadium_props,
         narr="Anything already moving just keeps going. Nothing slows it DOWN.", n_at=36.7,
         say="I'm never STOPPING!", say_at=38.8, pitch=560),
    dict(id="twist", s=BACK, e=50.0, bg="gully", clock="5 SEC · FRICTION BACK", char="uncle", state="angry",
         pos=(540, 1040, 560), props=pile, twist=True, look=(0, 0.3),
         narr="Friction returns. Everything skids to a stop in one big PILE.", n_at=43.3,
         say="Where did my CHAPPALS go?!", say_at=45.4, pitch=220),
    dict(id="outro", s=50.0, e=55.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 260 * math.sin((T - 1.9) * 2.2)
        spr = draw_char("auto", 340, T, 0, False, (0, 0), 1).rotate(8 * math.sin(T * 6), resample=Image.BICUBIC)
        paste_c(frame, spr, x, 1400, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=55.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("FRICTION", WHITE)], 150), 770, 0.75, "right"),
        (title([("DISAPPEARED", WHITE)], 130), 915, 1.05, "left"),
        (title([("...for ", WHITE), ("5 SECONDS?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("grab first?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("auto", 1), ("chai", 1), ("football", 1), ("uncle", "angry")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=10.3), dict(t0=10.6, t1=42.85, minor=True, melody=True),
           dict(t0=50.0, t1=55.0, melody=True)],
    fx=[("slide", OFF + 0.2, 0.8, dict(dd=6.0)), ("autohorn", 17.5, 1.0), ("screech", 18.3, 0.6),
        ("autohorn", 21.5, 0.7), ("slide", 23.6, 0.6, dict(dd=6.0)), ("sproing", 24.6, 0.8), ("sproing", 26.9, 0.6),
        ("sproing", 31.0, 0.7), ("whistle", 36.8, 0.6), ("crowd", 36.6, 0.4, dict(dd=6.0)),
        ("crash", BACK + 0.3, 1.1), ("boom", BACK + 0.35, 0.6)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_friction_disappeared")
