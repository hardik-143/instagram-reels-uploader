#!/usr/bin/env python3
"""What if you sent a samosa back to the dinosaurs?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

LAND = 4.9
IMPACT = 31.0

@E.sfx
def roar():
    t = E.tarr(1.4); f = 90 + 40 * np.sin(np.pi * t / 1.4)
    ph = E.osc(f); n = E.lp(E.noise(len(t)), 6)
    s = np.tanh(2 * (np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sin(3 * ph))) * 0.6 + n * 0.8
    return E.lp(s, 4) * np.minimum(1, t / 0.15) * np.minimum(1, (1.4 - t) / 0.4) * 0.6

@E.sfx
def honk():
    t = E.tarr(0.6); f = 220 - 40 * t
    s = np.sign(np.sin(E.osc(f))) * 0.4 + np.sin(E.osc(f * 2)) * 0.3
    return E.lp(s, 6) * np.minimum(1, t / 0.03) * np.minimum(1, (0.6 - t) / 0.1) * 0.45

@E.sfx
def crunch():
    s = np.zeros(int(0.6 * E.SR))
    for k in range(5):
        i = int(k * 0.1 * E.SR); n = E.noise(1800); n = n - E.lp(n, 3)
        s[i:i + 1800] += n * np.exp(-np.arange(1800) / 400) * 0.5
    return s

@E.sfx
def thud():
    t = E.tarr(0.5); return np.sin(E.osc(70 + 80 * np.exp(-t * 20))) * np.exp(-t * 9) * 0.9

@E.sfx
def portal():
    t = E.tarr(1.0); f = 300 + 900 * t
    return np.sin(E.osc(f)) * np.sin(E.osc(np.full(len(t), 6.0))) * np.sin(np.pi * t) * 0.25

def portal_rings(d, cx, cy, T, s=1.0):
    for k in range(4):
        r = (60 + k * 40 + (T * 120) % 40) * s
        d.ellipse([cx - r, cy - r * 0.35, cx + r, cy + r * 0.35], outline=[(160, 90, 255), (90, 200, 255), (255, 120, 220), (255, 214, 10)][k], width=8)

def intro_extra(frame, d, T):
    if T < 1.9: return
    if T < 3.1:
        paste_c(frame, draw_char("samosa", 360, T, 0, False, (0, 0), 1), 540, 1380, ease_back((T - 1.9) / 0.4))
    else:
        q = clamp((T - 3.1) / 0.7)
        portal_rings(d, 540, 1440, T, 1.2)
        spr = draw_char("samosa", 360, T, 0, False, (0, 0), 1).rotate(q * 720, resample=Image.BICUBIC)
        paste_c(frame, spr, 540, 1380 + 60 * q, max(0.02, 1 - q))

def land_pos(T):
    if T < LAND:
        q = clamp((T - 4.0) / (LAND - 4.0))
        return (540, -200 + (1110 + 200) * q * q, 560)
    b = 60 * math.exp(-(T - LAND) * 6) * abs(math.sin((T - LAND) * 12))
    return (540, 1110 - b, 560)

def land_props(frame, d, T, sc):
    if T < LAND + 0.4:
        portal_rings(d, 540, 160, T, 1.0)

def small_samosa(frame, d, T, sc, x=860, y=1270):
    comp(frame, draw_char("samosa", 170, T, 0, False, (-0.6, 0), 1), x - 85, y - 85)

def trike_after(frame, d, T, sc):
    small_samosa(frame, d, T, sc, 880, 1270)

def asteroid_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 0.6) / (IMPACT - sc["s"] - 0.6))
    ax, ay = 1080 - 760 * q, 200 + 700 * q
    r = 20 + 110 * q
    for i in range(14):
        tx, ty = ax + (i + 1) * 30 * (1 + q), ay - (i + 1) * 26 * (1 + q)
        rr = r * (1 - i / 14)
        d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=(255, 180 - i * 8, 60))
    d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=(90, 70, 60), outline=(255, 120, 40), width=8)

def flash(frame, T, sc):
    if T >= IMPACT:
        a = clamp((T - IMPACT) / 0.5)
        frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 250, 230, 255)), a)
    return frame

FOSSIL = Image.new("RGBA", (220, 200), (0, 0, 0, 0))
_d = ImageDraw.Draw(FOSSIL)
_d.polygon([(110, 10), (210, 190), (10, 190)], fill=(150, 140, 130), outline=(90, 84, 78), width=6)
_d.line([(110, 18), (110, 186)], fill=(110, 104, 98), width=4)
for x, y in ((70, 160), (150, 160), (110, 90)):
    _d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(110, 104, 98))

def dig_props(frame, d, T, sc):
    comp(frame, FOSSIL, 540 - 110, 1690 - 100)
    if (T * 2) % 1 < 0.5:
        for a in range(0, 360, 45):
            ra = math.radians(a); d.line([(540 + 120 * math.cos(ra), 1690 + 90 * math.sin(ra)), (540 + 150 * math.cos(ra), 1690 + 112 * math.sin(ra))], fill=YEL, width=6)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="land", s=4.0, e=11.0, bg="cretaceous", clock="66 MILLION YEARS AGO", char="samosa", pos=land_pos,
         enter=3.0, props=land_props, look=(0.3, -0.3),
         narr="A samosa lands 66 million years in the past.", n_at=5.2,
         say="Hello? Where's the CHUTNEY?", say_at=6.6, pitch=560),
    dict(id="trex", s=11.0, e=18.0, bg="cretaceous", clock="T. REX", char="trex", pos=(470, 1060, 620),
         props_after=small_samosa, look=(0.8, 0.5),
         narr="A T. rex smells it first. Its nose was incredible.", n_at=11.2,
         say="My arms are too SHORT to reach it!", say_at=12.9, pitch=150),
    dict(id="trike", s=18.0, e=25.0, bg="cretaceous", clock="TRICERATOPS", char="trike", pos=(470, 1060, 600),
         props_after=trike_after, look=(0.8, 0.5),
         narr="A Triceratops takes a bite. Fun fact: potatoes didn't exist yet!", n_at=18.2,
         say="Whatever this is... I LOVE it.", say_at=20.2, pitch=260),
    dict(id="asteroid", s=25.0, e=32.0, bg="cretaceous", clock="THE SKY", char="samosa", pos=(540, 1110, 520),
         props=asteroid_props, overlay=flash, look=(0.6, -0.8),
         narr="Then a 10 km wide asteroid shows up.", n_at=25.2,
         say="Was it something I SAID?", say_at=26.9, pitch=560),
    dict(id="dig", s=32.0, e=39.0, bg="digsite", clock="66 MILLION YEARS LATER", char="uncle", state="hat",
         pos=(540, 1060, 560), props=dig_props, look=(0, 0.8),
         narr="Millions of years later, a paleontologist digs up a fossil...", n_at=32.2,
         say="A FOSSIL samosa?! Still crispy.", say_at=34.4, pitch=230),
    dict(id="outro", s=39.0, e=44.0),
]

cfg = dict(
    total=44.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU SENT A", WHITE)], 130), 770, 0.75, "right"),
        (title([("SAMOSA BACK", YEL)], 130), 915, 1.05, "left"),
        (title([("...to the ", WHITE), ("DINOSAURS?", YEL)], 84), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL), (" send", WHITE)], 96), 470, 0.15),
                      (title([("back in time?", YEL)], 116), 600, 0.45)],
               row=[("samosa", 1), ("trex", 1), ("trike", 1), ("uncle", "hat"), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=31.0, minor=True), dict(t0=39.0, t1=44.0, melody=True)],
    fx=[("portal", 3.1, 1.0), ("whoosh", 4.2, 0.8), ("thud", LAND, 1.0),
        ("roar", 11.2, 1.0), ("honk", 18.3, 1.0), ("crunch", 21.9, 1.0),
        ("rumble", 25.5, 0.9, dict(dd=5.6)), ("boom", IMPACT, 1.3), ("rumble", IMPACT, 1.0, dict(dd=1.2)),
        ("wind", 32.0, 0.35, dict(dd=7.0)), ("ding", 36.3, 1.0)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_sent_a_samosa_to_the_dinosaurs")
