#!/usr/bin/env python3
"""What if you caught a shooting star? (Orionid meteor shower, October 2026)"""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def streak(d, x, y, ln, ang, w=6, col=(255, 250, 220)):
    dx, dy = math.cos(ang), math.sin(ang)
    for i in range(8):
        f = i / 8
        r = w * (1 - f) + 1
        px, py = x - dx * ln * f, y - dy * ln * f
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 250 - int(60 * f), 220 - int(120 * f)))

def meteors(frame, d, T, sc, n=4, speed=1.0):
    ang = math.radians(150)
    for k in range(n):
        ph = (T * 0.45 * speed + k / n) % 1.0
        if ph > 0.45: continue
        q = ph / 0.45
        x0 = 980 - k * 170; y0 = 380 + (k % 2) * 140
        x = x0 + math.cos(ang) * 520 * q; y = y0 + math.sin(ang) * 520 * q
        streak(d, x, y, 180 * min(1, q * 3), ang + math.pi, w=7)

def sky_props(frame, d, T, sc):
    meteors(frame, d, T, sc, n=4)

def dust_props(frame, d, T, sc):
    # an open palm with a tiny glowing speck, plus a sand grain for scale
    cx, cy = 820, 1230
    d.ellipse([cx - 120, cy - 60, cx + 120, cy + 60], fill=(242, 194, 152), outline=OUTL, width=6)
    g = 6 + 2 * math.sin(T * 6)
    d.ellipse([cx - g - 8, cy - g - 8, cx + g + 8, cy + g + 8], fill=(255, 220, 120))
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(90, 70, 60))
    l = label("~1 MM", 44, YEL)
    comp(frame, l, cx - l.width / 2, cy - 140)

def speed_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(10):
        y = 700 + k * 70
        x = (1200 - (lt * 2400 + k * 330) % 1600)
        d.line([(x, y), (x + 160, y)], fill=(170, 190, 255), width=5)
    x = 1100 - 1000 * ((lt * 0.9) % 1.3)
    streak(d, x, 1260, 260, 0, w=12)

def height_props(frame, d, T, sc):
    # a ruler on the left: 0 to 120 km
    x = 120
    d.line([(x, 860), (x, 1330)], fill=WHITE, width=6)
    for km in (0, 50, 100):
        y = 1330 - km * 4.3
        d.line([(x - 20, y), (x + 20, y)], fill=WHITE, width=6)
        l = label(f"{km} KM", 40, YEL if km else WHITE)
        comp(frame, l, x + 30, y - l.height / 2)
    # a meteor glowing between ~100 and 50 km, fading out
    lt = T - sc["s"]
    ph = (lt * 0.35) % 1.0
    y = 1330 - (100 - 50 * ph) * 4.3
    if ph < 0.9:
        streak(d, 330, y, 160, math.pi / 2, w=int(10 * (1 - ph)) + 2)

def blink_props(frame, d, T, sc):
    meteors(frame, d, T, sc, n=2, speed=2.2)

def comet(d, cx, cy, s=1.0, T=0):
    for i in range(14):
        f = i / 14
        r = (60 - 30 * f) * s
        x = cx + 60 * i * s; y = cy - 26 * i * s + 6 * math.sin(T * 2 + i)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(160 + int(80 * f), 220, 255))
    d.ellipse([cx - 40 * s, cy - 40 * s, cx + 40 * s, cy + 40 * s], fill=(240, 250, 255), outline=OUTL, width=5)

def halley_props(frame, d, T, sc):
    lt = T - sc["s"]
    comet(d, 180 + 20 * math.sin(T), 500, 0.9, T)
    for k in range(30):
        x = (k * 131 + lt * 30) % W; y = 640 + (k * 89) % 260
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(200, 220, 255))

def watch_props(frame, d, T, sc):
    meteors(frame, d, T, sc, n=5, speed=0.8)
    d.rectangle([0, 1640, W, H], fill=(30, 40, 60))

def twist_props(frame, d, T, sc):
    comet(d, 860, 420, 0.6, T)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wish", s=4.0, e=11.0, bg="night", clock="OCTOBER NIGHT", char="kid", pos=(540, 1080, 520),
         props=sky_props, look=(0.4, -0.5),
         narr="Every October, shooting stars streak across the night sky.", n_at=4.2,
         say="I'm going to CATCH one!", say_at=6.8, pitch=600),
    dict(id="dust", s=11.0, e=18.0, bg="night", clock="SIZE: ~1 MM", char="kid", pos=(420, 1080, 480),
         props_after=dust_props, look=(0.6, 0.3),
         narr="You'd be holding... a speck of DUST. Most are the size of a grain of SAND.", n_at=11.2,
         say="THAT'S the star?!", say_at=14.4, pitch=620),
    dict(id="speed", s=18.0, e=25.0, bg="space", clock="66 KM PER SECOND", char="earth", pos=(540, 1000, 440),
         props=speed_props, look=(0.5, 0),
         narr="This dust hits our air at 66 KM a SECOND. Delhi to Mumbai in under 20 SECONDS.", n_at=18.2,
         say="Slow DOWN, guest!", say_at=21.4, pitch=200),
    dict(id="height", s=25.0, e=32.0, bg="night", clock="~100 KM UP", char="kid", pos=(680, 1080, 460),
         props=height_props, look=(-0.4, -0.4),
         narr="It glows around 100 KM up, and burns away before 50 KM.", n_at=25.2,
         say="Ladder kitna LAMBA chahiye?", say_at=28.0, pitch=600),
    dict(id="blink", s=32.0, e=39.0, bg="night", clock="~1 SECOND", char="kid", pos=(540, 1080, 500),
         props=blink_props, look=(-0.3, -0.5),
         narr="And most shooting stars glow for only about one SECOND.", n_at=32.2,
         say="I BLINKED. Gone!", say_at=34.8, pitch=620),
    dict(id="halley", s=39.0, e=46.0, bg="space", clock="HALLEY'S COMET", char="earth", pos=(640, 1100, 420),
         props=halley_props, look=(-0.5, -0.3),
         narr="October's shower, the ORIONIDS, is crumbs from HALLEY'S COMET.", n_at=39.2,
         say="I drive through its MESS every year.", say_at=42.0, pitch=200),
    dict(id="watch", s=46.0, e=53.0, bg="night", clock="21-22 OCTOBER", char="kid", pos=(540, 1080, 480),
         props=watch_props, look=(0.3, -0.5),
         narr="Peak: around 21-22 OCTOBER. Look up before DAWN, after the Moon sets.", n_at=46.2,
         say="Alarm set for 3 AM!", say_at=49.4, pitch=600),
    dict(id="twist", s=53.0, e=61.0, bg="night", clock="THE CATCH", char="kid", pos=(540, 1080, 520),
         props=twist_props, twist=True, look=(0.5, -0.4),
         narr="You can't catch the dust... but Halley itself comes back in 2061.", n_at=53.2,
         say="Calendar mein NOTE kar lo!", say_at=56.6, pitch=600),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.5:
        q = clamp((T - 1.5) / 1.2)
        ang = math.radians(150)
        streak(d, 1000 + math.cos(ang) * 700 * q, 1250 + math.sin(ang) * 700 * q, 260, ang + math.pi, w=12)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU CAUGHT", WHITE)], 130), 770, 0.75, "right"),
        (title([("A SHOOTING", WHITE)], 130), 910, 1.05, "left"),
        (title([("STAR?", YEL)], 130), 1055, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("How old will ", WHITE), ("YOU", YEL)], 92), 470, 0.15),
                      (title([("be in 2061?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("earth", 1), ("moon", 1), ("sun", 1), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=39.0, melody=True), dict(t0=39.0, t1=52.85, minor=True),
           dict(t0=61.0, t1=66.0, melody=True)],
    drones=[dict(t0=18.0, dur=7.0, g=0.06), dict(t0=39.0, dur=7.0, g=0.06)],
    fx=[("whoosh", 1.6, 0.8), ("whoosh", 5.0, 0.5), ("whoosh", 18.6, 0.9), ("whoosh", 33.0, 0.6),
        ("whoosh", 47.0, 0.5), ("ding", 49.6, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_caught_a_shooting_star")
