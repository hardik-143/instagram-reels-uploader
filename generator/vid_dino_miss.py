#!/usr/bin/env python3
"""What if the dinosaur asteroid had missed Earth? Chicxulub, 66 million years ago, ~10 km, ~75% of species gone.
Dinos had ~165 million years already; mammals stayed small; India was an island (Rajasaurus).
Twist: dinosaurs never fully died out -- about 11,000 bird species are living dinosaurs."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def rock(d, ax, ay, r, q, tail_dx=30, tail_dy=-26):
    for i in range(14):
        tx, ty = ax + (i + 1) * tail_dx * (1 + q), ay + (i + 1) * tail_dy * (1 + q)
        rr = r * (1 - i / 14)
        d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=(255, 180 - i * 8, 60))
    d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=(90, 70, 60), outline=(255, 120, 40), width=8)

def impact_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 0.5) / 6.5)
    rock(d, 1000 - 500 * q, 420 + 260 * q, 18 + 50 * q, q)

def miss_props(frame, d, T, sc):
    # asteroid sweeps past Earth (at 540, 1100) and away to the right
    lt = T - sc["s"]
    q = clamp((lt - 0.4) / 4.0)
    ang = math.pi * (1.15 - 0.9 * q)
    ax = 540 + 430 * math.cos(ang); ay = 1000 - 380 * math.sin(ang) + 300 * q
    rock(d, ax, ay, 40, 0.3, tail_dx=-24 * math.sin(ang), tail_dy=-24 * math.cos(ang))
    if lt > 4.6:
        l = label("MISSED!", 70, YEL)
        comp(frame, l, 540 - l.width / 2, 380)

def mouse(d, x, y, s=1.0, T=0):
    bob = 4 * math.sin(T * 9)
    y += bob
    d.line([(x + 70 * s, y + 10 * s), (x + 130 * s, y - 20 * s), (x + 160 * s, y + 5 * s)], fill=(200, 140, 150), width=int(7 * s))
    d.ellipse([x - 80 * s, y - 45 * s, x + 80 * s, y + 40 * s], fill=(160, 150, 150), outline=OUTL, width=5)
    d.ellipse([x - 120 * s, y - 40 * s, x - 40 * s, y + 25 * s], fill=(170, 160, 160), outline=OUTL, width=5)
    for ex in (-95, -60):
        d.ellipse([x + (ex - 22) * s, y - 85 * s, x + (ex + 22) * s, y - 35 * s], fill=(240, 180, 190), outline=OUTL, width=4)
    d.ellipse([x - 100 * s, y - 18 * s, x - 86 * s, y - 4 * s], fill=(20, 20, 30))
    d.ellipse([x - 128 * s, y - 14 * s, x - 112 * s, y + 2 * s], fill=(230, 100, 120))

def mammal_props(frame, d, T, sc):
    mouse(d, 250, 1240, 1.3, T)
    l = label("MOUSE-SIZED", 58, YEL)
    comp(frame, l, 250 - l.width / 2, 1060)

def crown(d, cx, cy, w=150):
    h = w * 0.6
    pts = [(cx - w / 2, cy), (cx - w / 2, cy - h), (cx - w / 4, cy - h * 0.45), (cx, cy - h),
           (cx + w / 4, cy - h * 0.45), (cx + w / 2, cy - h), (cx + w / 2, cy)]
    d.polygon(pts, fill=(255, 205, 40), outline=OUTL)
    d.line(pts + [pts[0]], fill=OUTL, width=6)
    for x in (cx - w / 2, cx, cx + w / 2):
        d.ellipse([x - 12, cy - h - 12, x + 12, cy - h + 12], fill=(230, 50, 60), outline=OUTL, width=3)

CROWN_AT = (540, 912)
def india_after(frame, d, T, sc):
    bob = 8 * math.sin(T * 3.2)
    crown(d, CROWN_AT[0], CROWN_AT[1] + bob, 150)

def india_props(frame, d, T, sc):
    l = label("FOSSILS FOUND IN GUJARAT", 54, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

def human_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 3.0:
        l = label("NO CRICKET?", 62, YEL)
        comp(frame, l, 540 - l.width / 2, 380)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="impact", s=4.0, e=11.0, bg="cretaceous", clock="66 MILLION YEARS AGO", char="trex",
         pos=(380, 1080, 560), props=impact_props, look=(0.6, -0.6),
         narr="66 MILLION years ago, a rock about 10 KM wide hit Mexico at over 60,000 KM/H.", n_at=4.2,
         say="Ooh, a SHOOTING star!", say_at=7.4, pitch=150),
    dict(id="miss", s=11.0, e=18.0, bg="space", clock="WHAT IF IT MISSED?", char="earth",
         pos=(540, 1100, 380), props=miss_props, look=(0.4, -0.4), state=lambda T: T * 10,
         narr="Now imagine it MISSES. About 3/4 of all species no longer die out.", n_at=11.2,
         say="Phew! That was CLOSE.", say_at=15.4, pitch=220),
    dict(id="reign", s=18.0, e=25.0, bg="cretaceous", clock="165 MILLION YEARS", char="trike",
         pos=(540, 1080, 580),
         narr="Dinosaurs had already been around for about 165 MILLION years. Why stop now?", n_at=18.2,
         say="We're NOT going anywhere.", say_at=21.4, pitch=260),
    dict(id="mammals", s=25.0, e=32.0, bg="cretaceous", clock="OUR ANCESTORS", char="trex",
         pos=(720, 1060, 540), props=mammal_props, look=(-0.7, 0.3),
         narr="Most mammals back then were SMALL. With dinos still in charge, ours likely stay tiny.", n_at=25.2,
         say="Snack SIZE.", say_at=28.6, pitch=150),
    dict(id="india", s=32.0, e=39.0, bg="cretaceous", clock="INDIA, 66 MILLION YEARS AGO", char="trex",
         pos=(540, 1120, 560), props=india_props, props_after=india_after, look=(0, 0.2), bubble_y=700,
         narr="India was an ISLAND then, drifting north. Its own king dino: RAJASAURUS.", n_at=32.2,
         say="Call me RAJA.", say_at=35.4, pitch=160),
    dict(id="humans", s=39.0, e=46.0, bg="living", clock="TODAY?", char="kid", state="puff",
         pos=(540, 1080, 500), props=human_props,
         narr="Without that impact, humans might NEVER have evolved. No cricket. No SAMOSAS.", n_at=39.2,
         say="No SAMOSAS?!", say_at=42.0, pitch=620),
    dict(id="twist", s=46.0, e=53.0, bg="pigeon", clock="PLOT TWIST", char="pigeon", state="wink",
         pos=(540, 1080, 560), twist=True,
         narr="Twist: dinosaurs never fully vanished. About 11,000 kinds of BIRDS are living dinosaurs.", n_at=46.2,
         say="Respect your ELDERS.", say_at=49.6, pitch=420),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        paste_c(frame, draw_char("trex", 330, T, 0, False, (0.6, -0.3), 1), 420, 1420, p)
        q = clamp((T - 1.9) / 2.0)
        rock(d, 980 - 120 * q, 1260 - 60 * q, 34, 0.2)

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("THE DINO", WHITE)], 150), 770, 0.75, "right"),
        (title([("ASTEROID", WHITE)], 150), 915, 1.05, "left"),
        (title([("MISSED?", YEL)], 140), 1065, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" live", WHITE)], 104), 470, 0.15),
                      (title([("with dinosaurs?", YEL)], 104), 600, 0.45)],
               row=[("trex", 1), ("trike", 1), ("pigeon", 1), ("earth", 1), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, minor=True), dict(t0=11.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=45.85), dict(t0=53.0, t1=58.0, melody=True)],
    drones=[dict(t0=46.2, dur=6.5, g=0.05)],
    fx=[("rumble", 4.6, 0.6, dict(dd=6.0)), ("whoosh", 11.5, 0.8), ("whoosh", 14.0, 0.6), ("cheer", 15.6, 0.3),
        ("pop", 25.4, 0.6), ("ding", 32.5, 0.5), ("crowd", 39.2, 0.25, dict(dd=4.0)), ("gasp", 42.0, 0.6),
        ("kwak", 47.0, 0.6)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_the_dinosaur_asteroid_missed")
