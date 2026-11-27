#!/usr/bin/env python3
"""What if Earth were flat? Myth-busting physics thought experiment.
Sources: Gizmodo 'What If the Earth Suddenly Turned Flat?' (19 Jun 2017): Carol Finn (USGS) - toward the edges gravity
points toward the centre, 'like going up an increasingly steep hill'; Anders Sandberg (Oxford FHI) - air would rush to the
centre ('crazy storms and suffocation'), oceans pool in the middle; ships would not vanish bottom-first without curvature;
the Moon would get a straight, not curved, shadow from a disc seen edge-on; Dave Stevenson (Caltech) - a pancake Earth
'would want to go back to being a sphere ... on a timescale of an hour'. Physics World 'Fighting flat-Earth theory'
(Jul 2020): Eratosthenes, 3rd century BC, first to calculate Earth's circumference. Britannica 'Aryabhata I': the
Aryabhatiya (499 CE) holds that Earth is a sphere that rotates on its axis."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
LAND = (90, 180, 100)
SEA = (70, 140, 230)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def at_label(frame, txt, x, y, col=WHITE, size=56):
    l = label(txt, size, col)
    comp(frame, l, x - l.width / 2, y - l.height / 2)

def squashed_earth(frame, cx, cy, B, sy, T):
    """Earth character squashed vertically by factor sy (1 = round)."""
    spr = draw_char("earth", int(B), T, 0.0, False, (0, 0.1), T * 0.2)
    h = max(4, int(spr.height * sy))
    spr = spr.resize((spr.width, h), Image.BICUBIC)
    comp(frame, spr, cx - spr.width / 2, cy - h / 2)

def disc(d, cx, cy, rx, ry, thick=40, top=LAND):
    d.rectangle([cx - rx, cy, cx + rx, cy + thick], fill=(150, 110, 80))
    d.ellipse([cx - rx, cy + thick - ry, cx + rx, cy + thick + ry], fill=(150, 110, 80), outline=OUTL, width=6)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=top, outline=OUTL, width=6)
    d.line([(cx - rx, cy), (cx - rx, cy + thick)], fill=OUTL, width=6)
    d.line([(cx + rx, cy), (cx + rx, cy + thick)], fill=OUTL, width=6)

def arrow(d, x0, y0, x1, y1, col=YEL, w=10):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0); s = w * 2.6
    d.polygon([(x1 + math.cos(a) * s, y1 + math.sin(a) * s),
               (x1 + math.cos(a + 2.4) * s, y1 + math.sin(a + 2.4) * s),
               (x1 + math.cos(a - 2.4) * s, y1 + math.sin(a - 2.4) * s)], fill=col, outline=OUTL)

def ship(d, x, y, s=1.0):
    d.polygon([(x - 60 * s, y), (x + 60 * s, y), (x + 45 * s, y + 28 * s), (x - 45 * s, y + 28 * s)],
              fill=(200, 70, 60), outline=OUTL)
    d.rectangle([x - 25 * s, y - 34 * s, x + 25 * s, y], fill=WHITE, outline=OUTL, width=3)
    d.rectangle([x - 6 * s, y - 70 * s, x + 6 * s, y - 34 * s], fill=(60, 60, 70))

# ---------------------------------------------------------------- props
def flat_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.4) / 2.5))
    if lt < 3.0:
        squashed_earth(frame, 540, 1050, 480 + 200 * p, 1 - 0.8 * p, T)
    else:
        disc(d, 540, 1040, 330, 90)
        d.ellipse([400, 1000, 520, 1060], fill=SEA); d.ellipse([600, 1010, 720, 1070], fill=SEA)
    if lt > 0.4: top_label(frame, "A ROTI PLANET", 380, YEL, 100)

def ship_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.5) / 4.0))
    # top panel: curved Earth, ship sinks bottom-first behind the bulge
    d.rounded_rectangle([60, 640, 1020, 960], radius=30, fill=(170, 215, 250), outline=OUTL, width=6)
    sy = 866 + 52 * g
    ship(d, 760, sy, 0.9)
    d.chord([60, 860, 1020, 1060], 180, 360, fill=SEA, outline=OUTL, width=6)
    at_label(frame, "ROUND EARTH", 540, 690, WHITE, 46)
    # bottom panel: flat sea, ship only shrinks
    d.rounded_rectangle([60, 1010, 1020, 1330], radius=30, fill=(170, 215, 250), outline=OUTL, width=6)
    d.rectangle([66, 1200, 1014, 1324], fill=SEA)
    d.line([(66, 1200), (1014, 1200)], fill=OUTL, width=5)
    s2 = 1.0 - 0.75 * g
    ship(d, 300 + 400 * g, 1200 - 28 * s2, s2)
    at_label(frame, "FLAT DISC", 540, 1060, WHITE, 46)
    if lt > 0.4: top_label(frame, "WATCH THE SHIPS", 380, YEL, 92)

def grav_props(frame, d, T, sc):
    lt = T - sc["s"]
    disc(d, 540, 1120, 470, 120)
    for k, (ex, ey) in enumerate(((120, 1110), (960, 1110), (300, 1190), (780, 1190), (330, 1030), (750, 1030))):
        g = ease_out(clamp((lt - 0.5 - k * 0.15) / 0.6))
        tx = ex + (540 - ex) * 0.42 * g; ty = ey + (1120 - ey) * 0.42 * g + 40 * g
        if g > 0.05: arrow(d, ex, ey - 60, tx, ty - 20, YEL, 9)
    if lt > 2.6:
        spr = draw_char("kid", 200, T, 0.0, False, (-0.6, 0), "puff")
        spr = spr.rotate(-28, resample=Image.BICUBIC, expand=True)
        comp(frame, spr, 880 - spr.width / 2, 960 - spr.height / 2)
    if lt > 0.4: top_label(frame, "PULLED TO THE CENTRE", 380, YEL, 78)
    if lt > 3.0: at_label(frame, "EDGE = UPHILL", 540, 820, WHITE, 60)

def air_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.5) / 3.0))
    disc(d, 540, 1120, 470, 120)
    rx = 460 - 300 * g; ry = 115 - 70 * g
    d.ellipse([540 - rx, 1120 - ry, 540 + rx, 1120 + ry], fill=SEA, outline=OUTL, width=4)
    # air dome shrinking to the middle
    ar = 470 - 290 * g
    d.arc([540 - ar, 1120 - ar * 0.9, 540 + ar, 1120 + ar * 0.9], 180, 360, fill=(140, 220, 255), width=10)
    if lt > 3.4:
        at_label(frame, "NO AIR", 180, 970, (255, 120, 110), 56)
        at_label(frame, "NO AIR", 900, 970, (255, 120, 110), 56)
    if lt > 0.4: top_label(frame, "EVERYTHING SLIDES IN", 380, YEL, 80)

def moon_with_shadow(frame, cx, cy, B, T, kind):
    spr = draw_char("moon", B, T, 0.0, False, (0, 0.1))
    sh = Image.new("RGBA", spr.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    w, h = spr.size
    if kind == "round":
        sd.ellipse([-w * 0.55, -h * 0.15, w * 0.55, h * 1.15], fill=(120, 30, 20, 170))
    else:
        sd.rectangle([0, 0, w * 0.5, h], fill=(120, 30, 20, 170))
    mask = spr.split()[3]
    sh.putalpha(Image.composite(sh.split()[3], Image.new("L", spr.size, 0), mask))
    spr = spr.copy(); spr.alpha_composite(sh)
    comp(frame, spr, cx - w / 2, cy - h / 2)

def eclipse_props(frame, d, T, sc):
    lt = T - sc["s"]
    moon_with_shadow(frame, 290, 1060, 380, T, "round")
    if lt > 1.8: moon_with_shadow(frame, 790, 1060, 380, T, "straight")
    at_label(frame, "REAL: CURVED", 290, 820, WHITE, 50)
    if lt > 1.8: at_label(frame, "DISC: STRAIGHT", 790, 820, (255, 160, 150), 50)
    if lt > 0.4: top_label(frame, "LUNAR ECLIPSE", 380, YEL, 96)

def history_props(frame, d, T, sc):
    lt = T - sc["s"]
    # stick + shadow
    d.rectangle([60, 1180, 500, 1200], fill=(210, 180, 120), outline=OUTL, width=4)
    d.rectangle([150, 960, 166, 1180], fill=(120, 80, 50), outline=OUTL, width=3)
    d.polygon([(166, 1180), (166 + 180 * ease_out(clamp((lt - 0.5) / 1.5)), 1180), (166, 1168)], fill=(40, 40, 60))
    for k in range(3):
        d.line([(380 + k * 40, 760), (230 + k * 40, 1000)], fill=(255, 220, 110), width=6)
    at_label(frame, "~240 BC", 280, 1270, YEL, 60)
    if lt > 2.5:
        spr = draw_char("earth", 300, T, 0.0, False, (0, 0.1), T * 0.8)
        comp(frame, spr, 790 - 150, 1040 - 150)
        at_label(frame, "499 CE", 790, 1270, YEL, 60)
    if lt > 0.4: top_label(frame, "WE KNEW LONG AGO", 380, YEL, 86)

def hint_props(frame, d, T, sc):
    disc(d, 540, 1180, 380, 90)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.6) / 3.0))
    squashed_earth(frame, 540, 1060, 680 - 200 * p, 0.2 + 0.8 * p, T)
    if lt > 0.4: top_label(frame, "BACK TO A BALL", 380, YEL, 100)
    if lt > 3.2: at_label(frame, "IN ABOUT 1 HOUR", 540, 620, WHITE, 64)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="flat", s=4.0, e=11.0, bg="space", clock="SQUASH!", props=flat_props,
         narr="Squash EARTH into a giant flat DISC, like a ROTI. What changes?", n_at=4.2, narr_y=1560),
    dict(id="ships", s=11.0, e=18.0, bg="space", clock="AT THE BEACH", props=ship_props,
         narr="Today, ships vanish BOTTOM FIRST over the horizon. On a disc they'd just SHRINK.",
         n_at=11.2, narr_y=1560),
    dict(id="grav", s=18.0, e=25.0, bg="space", clock="GRAVITY", props=grav_props,
         narr="Gravity would pull toward the disc's CENTRE. Walking out feels like a STEEPER HILL.",
         n_at=18.2, narr_y=1560),
    dict(id="air", s=25.0, e=32.0, bg="space", clock="WEATHER", props=air_props,
         narr="AIR and OCEANS would rush to the MIDDLE. The edges? Barely any air.",
         n_at=25.2, narr_y=1560),
    dict(id="eclipse", s=32.0, e=39.0, bg="space", clock="NIGHT SKY", props=eclipse_props,
         narr="Eclipse shadows on the Moon are always CURVED. A disc side-on casts a STRAIGHT one.",
         n_at=32.2, narr_y=1560),
    dict(id="history", s=39.0, e=46.0, bg="space", clock="HISTORY", props=history_props,
         narr="ERATOSTHENES measured Earth's size using SHADOWS. In 499 CE, ARYABHATA wrote that it SPINS.",
         n_at=39.2, narr_y=1560),
    dict(id="hint", s=46.0, e=TW, bg="space", clock="BIG QUESTION", props=hint_props,
         char="uncle", state="hat", pos=(540, 960, 380),
         narr="Okay, but could a flat Earth at least STAY flat?", n_at=46.2, narr_y=1560,
         say="Surely it can STAY flat?", say_at=48.6, pitch=150),
    dict(id="twist", s=TW, e=60.5, bg="space", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: NO! GRAVITY would crush it back into a BALL. That's why planets are ROUND.",
         n_at=TW + 0.2, narr_y=1560),
    dict(id="outro", s=60.5, e=65.5),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        sq = 1 - 0.7 * ease_out(clamp((T - 2.6) / 1.0))
        squashed_earth(frame, 540, 1400, 300 * p + 4, sq, T)

cfg = dict(
    total=65.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EARTH WERE", WHITE)], 120), 770, 0.75, "right"),
        (title([("FLAT?", YEL)], 160), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which proof ", WHITE), ("YOU", YEL)], 100), 470, 0.15),
                      (title([("like best?", YEL)], 96), 600, 0.45)],
               row=[("earth", 1), ("moon", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0, minor=True), dict(t0=32.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.5, t1=65.5, melody=True)],
    drones=[dict(t0=25.0, dur=7.0, g=0.15)],
    fx=[("boom", 5.0, 0.25), ("waves", 11.3, 0.2, dict(dd=6.0)), ("wind", 25.3, 0.25, dict(dd=6.0)),
        ("tick", 40.0, 0.3), ("ding", 42.0, 0.2), ("rumble", TW + 0.7, 0.3, dict(dd=3.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_earth_were_flat")
