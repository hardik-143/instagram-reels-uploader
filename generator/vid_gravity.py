#!/usr/bin/env python3
"""What if gravity switched off for 5 seconds... in a Mumbai local?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

OFF = 10.5      # gravity switches off (scene 2 start)
BACK = 30.0     # gravity returns (twist)

@E.sfx
def clack(dd=6.0):
    s = np.zeros(int(dd * E.SR)); t = E.tarr(0.06)
    hit = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 60) + E.noise(len(t)) * np.exp(-t * 80) * 0.4
    k = 0.0
    while k < dd - 0.2:
        for off in (0, 0.12):
            i = int((k + off) * E.SR); s[i:i + len(hit)] += hit
        k += 0.9
    return s * 0.35 + E.lp(E.noise(len(s)), 80) * 1.2 * 0.25

@E.sfx
def zerog():
    t = E.tarr(1.4); f = 200 + 600 * (t / 1.4) ** 0.5
    s = np.sin(E.osc(f)) + 0.5 * np.sin(E.osc(f * 1.5))
    return s * np.sin(np.pi * t / 1.4) * 0.2

def sprite(w, h, draw):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); draw(ImageDraw.Draw(im), w, h); return im

def _bag(d, w, h):
    d.arc([w * 0.3, 0, w * 0.7, h * 0.5], 180, 360, fill=OUTL, width=8)
    d.rounded_rectangle([4, h * 0.25, w - 4, h - 4], radius=18, fill=(70, 110, 190), outline=OUTL, width=6)
    d.rectangle([w * 0.2, h * 0.5, w * 0.8, h * 0.62], fill=(250, 214, 10))
def _dabba(d, w, h):
    for k in range(3):
        y = 20 + k * (h - 30) / 3
        d.rounded_rectangle([6, y, w - 6, y + (h - 30) / 3 - 4], radius=10, fill=(206, 212, 222), outline=OUTL, width=5)
    d.line([(w / 2, 4), (w / 2, 24)], fill=OUTL, width=6); d.line([(w * 0.3, 6), (w * 0.7, 6)], fill=OUTL, width=6)
def _shoe(d, w, h):
    d.rounded_rectangle([4, h * 0.3, w - 4, h - 6], radius=20, fill=(230, 80, 70), outline=OUTL, width=6)
    d.rectangle([4, h - 26, w - 4, h - 6], fill=WHITE, outline=OUTL, width=5)
    for x in range(int(w * 0.3), int(w * 0.7), 18): d.line([(x, h * 0.35), (x + 12, h * 0.5)], fill=WHITE, width=4)
def _paper(d, w, h):
    d.rectangle([4, 4, w - 4, h - 4], fill=(244, 240, 228), outline=OUTL, width=5)
    d.rectangle([14, 14, w - 14, 40], fill=(60, 60, 70))
    for y in range(52, h - 14, 16): d.line([(14, y), (w - 14, y)], fill=(170, 170, 176), width=4)

ITEMS = [sprite(140, 150, _bag), sprite(110, 150, _dabba), sprite(150, 90, _shoe), sprite(130, 160, _paper), E.R.PHONE]
BASES = [(140, 600, 18), (930, 520, -14), (220, 1180, 24), (880, 1200, -20), (720, 380, 30), (330, 380, -26)]

def floating(frame, d, T, sc, n=6):
    t = T - OFF
    for i in range(n):
        bx, by, sp = BASES[i]
        spr = ITEMS[i % len(ITEMS)]
        x = bx + 40 * math.sin(T * 0.7 + i * 1.3)
        y = by - 14 * t * (1 + (i % 3) * 0.3) + 20 * math.sin(T * 1.1 + i)
        rot = sp * t
        r = spr.rotate(rot, resample=Image.BICUBIC, expand=True)
        comp(frame, r, x - r.width / 2, y - r.height / 2)

def fallen(frame, d, T, sc):
    q = clamp((T - BACK) / 0.35)
    for i, (fx, fy, rot) in enumerate([(130, 1700, 80), (950, 1720, -10), (360, 1800, 15), (800, 1820, 95), (620, 1720, 40)]):
        spr = ITEMS[i % len(ITEMS)].rotate(rot, resample=Image.BICUBIC, expand=True)
        y = 200 + (fy - 200) * q * q
        comp(frame, spr, fx - spr.width / 2, y - spr.height / 2)

def uncle_pos(T):
    t = T - OFF
    return (540 + 60 * math.sin(T * 0.8), 1060 - 18 * t, 560)

def uncle_rot(T):
    return 25 * math.sin((T - OFF) * 0.9)

def chai_pos(T):
    return (540 + 40 * math.sin(T * 1.3), 1040 + 30 * math.sin(T * 0.9), 520)

def droplets(frame, d, T, sc):
    floating(frame, d, T, sc, 4)
    for k in range(7):
        a = T * 0.8 + k * 0.9
        x = 540 + (300 + 30 * math.sin(T + k)) * math.cos(a); y = 1040 + 220 * math.sin(a)
        r = 10 + (k % 3) * 5
        d.ellipse([x - r, y - r, x + r, y + r], fill=(198, 130, 72), outline=OUTL, width=3)

def pigeon_pos(T):
    return (540 + 50 * math.sin(T * 1.1), 1050 + 25 * math.sin(T * 1.7), 540)

def intro_extra(frame, d, T):
    if T < 1.9: return
    spr = draw_char("uncle", 340, T, 0, False, (0, -0.5), 1).rotate(20 * math.sin(T * 2), resample=Image.BICUBIC)
    paste_c(frame, spr, 540, 1400 - 40 * (T - 1.9), ease_back((T - 1.9) / 0.4))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="packed", s=4.0, e=10.5, bg="train", clock="8:47 AM", char="kid", pos=(540, 1080, 560), look=(0.5, 0),
         narr="8:47 AM. Virar fast local. Packed, as usual.", n_at=4.2,
         say="I can't even move my ARM.", say_at=5.9, pitch=600),
    dict(id="float", s=10.5, e=17.0, bg="train", clock="GRAVITY OFF · 1 SEC", char="uncle", pos=uncle_pos, rot=uncle_rot,
         props=floating, look=(0, -0.6),
         narr="Gravity switches off. Everyone starts FLOATING.", n_at=10.7,
         say="Finally... PERSONAL space!", say_at=12.4, pitch=230),
    dict(id="chai", s=17.0, e=23.5, bg="train", clock="2 SEC", char="chai", pos=chai_pos, props=droplets,
         narr="Your cutting chai turns into a floating BALL.", n_at=17.2,
         say="Don't drink me... CATCH me!", say_at=18.9, pitch=520),
    dict(id="coast", s=23.5, e=30.0, bg="train", clock="4 SEC", char="pigeon", pos=pigeon_pos,
         props=lambda f, d, T, sc: floating(f, d, T, sc, 6), look=(0.4, 0.2),
         narr="No weight means no grip. The wheels just keep coasting.", n_at=23.7,
         say="Welcome to OUR world, humans.", say_at=25.5, pitch=660),
    dict(id="back", s=30.0, e=37.0, bg="train", clock="5 SEC", char="kid", pos=(330, 1110, 540), twist=True,
         props=fallen, look=(-0.7, 0.1),
         narr="Then gravity comes BACK...", n_at=30.3,
         say="...and I landed in a WINDOW SEAT!", say_at=32.0, pitch=600),
    dict(id="outro", s=37.0, e=42.0),
]

cfg = dict(
    total=42.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("GRAVITY", WHITE)], 150), 770, 0.75, "right"),
        (title([("SWITCHED OFF", WHITE)], 124), 915, 1.05, "left"),
        (title([("...in a ", WHITE), ("MUMBAI LOCAL?", YEL)], 80), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Where would ", WHITE), ("YOU", YEL), (" be?", WHITE)], 96), 470, 0.15),
                      (title([("Tell us below!", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("chai", 1), ("pigeon", 1), ("auto", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=10.3), dict(t0=10.6, t1=29.85, drums=False, minor=True),
           dict(t0=37.0, t1=42.0, melody=True)],
    fx=[("clack", 4.0, 0.9, dict(dd=6.4)), ("zerog", OFF, 1.0), ("whoosh", OFF + 0.3, 0.8),
        ("clack", 23.5, 0.5, dict(dd=6.3)), ("crash", BACK + 0.25, 1.1), ("thud", BACK + 0.3, 1.0) if "thud" in E.SFX else ("boom", BACK + 0.3, 0.7),
        ("clack", 32.0, 0.5, dict(dd=5.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_gravity_switched_off_in_a_mumbai_local")
