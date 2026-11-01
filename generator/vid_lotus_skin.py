#!/usr/bin/env python3
"""What if your skin worked like a lotus leaf?
Facts (Wikipedia 'Lotus effect' and sources therein): lotus leaves are superhydrophobic, water contact angle up to
about 170 deg, with only ~0.6% of the drop's area touching the leaf (2-3% for other plants near 160 deg). The surface has
papillae about 10-20 um tall and 10-15 um wide, covered in epicuticular wax. Rolling drops pick up dirt and dust:
self-cleaning (AskNature). Taro (Colocasia, 'arbi') leaves reach a contact angle of about 148 deg.
Sto Corp sells a 'Lotus-Effect' exterior coating whose microtextured superhydrophobic surface lets rain wash off dirt
(AskNature). Twist: the self-cleaning depends on water's high surface tension and does not work with organic solvents
(Wikipedia); 'essentially no naturally oleophobic materials exist' (Tuteja et al., MRS Bulletin 2008), so oily
fingers would still smudge it."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

LEAF, LEAF_D, VEIN = (96, 176, 96), (70, 140, 74), (150, 210, 140)
DROP, DROP_HI = (140, 200, 250), (230, 246, 255)

def leaf(d, cx, cy, rx, ry, col=LEAF):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col, outline=OUTL, width=8)
    for k in range(12):
        a = 2 * math.pi * k / 12
        d.line([(cx, cy), (cx + rx * 0.92 * math.cos(a), cy + ry * 0.92 * math.sin(a))], fill=VEIN, width=5)
    d.ellipse([cx - 16, cy - 10, cx + 16, cy + 10], fill=VEIN)

def drop(d, x, y, r, face=False, T=0.0, squash=1.0):
    ry = r * squash
    d.ellipse([x - r, y - 2 * ry + r * 0.15, x + r, y + r * 0.15], fill=DROP, outline=OUTL, width=6)
    cy = y - ry + r * 0.15
    d.ellipse([x - r * 0.55, cy - ry * 0.6, x - r * 0.15, cy - ry * 0.2], fill=DROP_HI)
    if face:
        for ex in (-0.3, 0.3):
            d.ellipse([x + ex * r - r * 0.09, cy - r * 0.05, x + ex * r + r * 0.09, cy + r * 0.2], fill=OUTL)
        d.arc([x - r * 0.2, cy + r * 0.1, x + r * 0.2, cy + r * 0.38], 20, 160, fill=OUTL, width=5)

def rain_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(10):
        x = (k * 113 + 60) % 1000 + 40
        ph = (lt * 0.9 + k * 0.137) % 1.0
        if 380 < x < 700 and ph > 0.55:
            # drops that hit the kid bounce off sideways as little balls
            q = (ph - 0.55) / 0.45
            sx = 1 if x > 540 else -1
            bx = x + sx * 260 * q
            by = 860 + 420 * q * q - 120 * q
            drop(d, bx, by, 24)
        else:
            y = 300 + ph * 1100
            drop(d, x, y, 22)
    if lt > 1.0: top_label(frame, "ZERO DROPS SOAK IN", 380, YEL, 64)

def ball_props(frame, d, T, sc):
    lt = T - sc["s"]
    leaf(d, 540, 1150, 470, 150)
    g = ease_back(clamp((lt - 0.4) / 0.6))
    if g > 0:
        r = 150 * g
        drop(d, 540, 1110, r, face=g > 0.9, T=T, squash=1.0 + 0.04 * math.sin(T * 6))
    if lt > 2.0:
        l = label("UP TO 170°", 90, YEL); comp(frame, l, 540 - l.width / 2, 560)
    if lt > 1.0: top_label(frame, "ALMOST A PERFECT BALL", 380, YEL, 60)

def zoom_circle(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 248, 236), outline=OUTL, width=10)

def bumps(d, cx, cy, r, base, n=7, wax=True):
    w = 2 * r * 0.8 / n
    x0 = cx - r * 0.8
    d.rectangle([cx - r * 0.86, base, cx + r * 0.86, cy + r * 0.62], fill=LEAF)
    for k in range(n):
        x = x0 + w * (k + 0.5)
        d.ellipse([x - w * 0.38, base - 90, x + w * 0.38, base + 30], fill=LEAF, outline=OUTL, width=5)
        if wax:
            for j in range(-2, 3):
                ax = x + j * w * 0.13
                d.line([(ax, base - 80 + abs(j) * 10), (ax + j * 3, base - 106 + abs(j) * 10)],
                       fill=(250, 250, 240), width=4)
    return base - 106

def bumps_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_back(clamp((lt - 0.3) / 0.5))
    if g <= 0: return
    cx, cy, r = 540, 860, 380 * g
    zoom_circle(d, cx, cy, r)
    if g > 0.9:
        bumps(d, cx, cy, r, cy + 120)
    if lt > 1.0: top_label(frame, "WAX-COATED BUMPS", 380, YEL, 66)

def air_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, r = 540, 860, 380
    zoom_circle(d, cx, cy, r)
    top = bumps(d, cx, cy, r, cy + 160)
    # a giant drop resting only on the bump tips; air pockets between
    la = label("AIR", 30, (200, 230, 255))
    for k in (1, 3, 5):
        x = cx - r * 0.8 + (2 * r * 0.8 / 7) * (k + 1)
        comp(frame, la, x - la.width / 2, top + 40 + 4 * math.sin(T * 3 + k))
    d.chord([cx - 300, top - 330, cx + 300, top + 30], 180, 360, fill=DROP, outline=OUTL, width=7)
    d.line([(cx - 296, top + 4), (cx + 296, top + 4)], fill=OUTL, width=7)
    d.ellipse([cx - 200, top - 270, cx - 110, top - 200], fill=DROP_HI)
    if lt > 1.0: top_label(frame, "ONLY 0.6% TOUCHES", 380, YEL, 66)

def clean_props(frame, d, T, sc):
    lt = T - sc["s"]
    # muddy pond
    d.rectangle([0, 1180, W, 1340], fill=(120, 96, 70))
    for k in range(9):
        d.ellipse([k * 130 - 20, 1200 + (k % 2) * 40, k * 130 + 60, 1230 + (k % 2) * 40], fill=(96, 76, 56))
    leaf(d, 540, 1000, 440, 140)
    # dirt specks get swallowed by a rolling drop
    q = clamp((lt - 1.0) / 4.5)
    dx = -380 + 760 * q
    for k in range(8):
        sx = -340 + k * 95
        if sx > dx: d.ellipse([540 + sx - 10, 990 - 8 + (k % 3) * 10, 540 + sx + 10, 990 + 8 + (k % 3) * 10],
                             fill=(110, 80, 50))
    r = 60 + 2 * sum(1 for k in range(8) if -340 + k * 95 <= dx)
    drop(d, 540 + dx, 1000, r, face=True, T=T)
    for k in range(8):
        if -340 + k * 95 <= dx:
            a = k * 1.3 + T * 2
            d.ellipse([540 + dx + 0.5 * r * math.cos(a) - 8, 1000 - r + 0.5 * r * math.sin(a) - 8,
                       540 + dx + 0.5 * r * math.cos(a) + 8, 1000 - r + 0.5 * r * math.sin(a) + 8], fill=(110, 80, 50))
    if lt > 1.0: top_label(frame, "SELF-CLEANING", 380, YEL, 72)

def arbi_leaf(d, cx, cy, s=1.0):
    pts = [(cx, cy - 300 * s), (cx + 260 * s, cy - 120 * s), (cx + 270 * s, cy + 80 * s), (cx + 60 * s, cy + 160 * s),
           (cx, cy + 60 * s), (cx - 60 * s, cy + 160 * s), (cx - 270 * s, cy + 80 * s), (cx - 260 * s, cy - 120 * s)]
    d.polygon(pts, fill=(70, 150, 80), outline=OUTL, width=8)
    for px, py in pts[1:4] + pts[5:]:
        d.line([(cx, cy - 20 * s), (px * 0.85 + cx * 0.15, py * 0.85 + (cy - 20 * s) * 0.15)], fill=VEIN, width=5)
    d.line([(cx, cy - 20 * s), (cx, cy - 280 * s)], fill=VEIN, width=6)
    d.line([(cx, cy + 60 * s), (cx, cy + 420 * s)], fill=(90, 130, 70), width=16)

def arbi_props(frame, d, T, sc):
    lt = T - sc["s"]
    arbi_leaf(d, 720, 880, 1.0)
    for k, (x, y, r) in enumerate(((640, 840, 40), (780, 760, 30), (700, 950, 26), (840, 900, 34))):
        if lt > 0.8 + k * 0.5:
            drop(d, x + 6 * math.sin(T * 3 + k), y, r)
    if lt > 1.0: top_label(frame, "ARBI (TARO) LEAF: ~148°", 380, YEL, 58)

def wall_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([150, 470, 930, 1200], fill=(250, 240, 222), outline=OUTL, width=8)
    for wx in (230, 600):
        d.rectangle([wx, 560, wx + 250, 780], fill=(170, 210, 240), outline=OUTL, width=6)
        d.line([(wx + 125, 560), (wx + 125, 780)], fill=OUTL, width=5)
    q = clamp((lt - 0.8) / 5.0)
    # dirt streaks above the rain line, clean wall below
    yl = 470 + 730 * q
    for k in range(10):
        x = 190 + k * 76
        d.line([(x, 820), (x + 8, 1170)], fill=(170, 150, 120), width=12)
    if yl > 820:
        d.rectangle([166, 816, 914, min(1184, yl)], fill=(250, 240, 222))
    for k in range(7):
        x = 200 + k * 110
        drop(d, x, 490 + ((lt * 600 + k * 170) % 700), 22)
    if lt > 1.0: top_label(frame, "LOTUS-EFFECT PAINT", 380, YEL, 64)

def samosa_props(frame, d, T, sc):
    lt = T - sc["s"]
    leaf(d, 540, 1180, 440, 130)
    # water beads up, the oil smear spreads flat
    drop(d, 360, 1150, 60)
    g = ease_out(clamp((lt - 1.5) / 1.2))
    if g > 0:
        d.ellipse([560, 1150 - 30 * g, 560 + 260 * g, 1150 + 30 * g], fill=(240, 200, 90), outline=OUTL, width=4)
    lw = label("WATER: BALL", 44, WHITE); comp(frame, lw, 360 - lw.width / 2, 960)
    if lt > 2.0:
        lo = label("OIL: SMEAR", 44, YEL); comp(frame, lo, 690 - lo.width / 2, 1040)
    if lt > 1.0: top_label(frame, "WATER YES, OIL NO", 380, YEL, 66)

S = [
    dict(id="intro", s=0.0, e=4.5),
    dict(id="rain", s=4.5, e=12.0, bg="storm", clock="MONSOON", char="kid", pos=(540, 1060, 460),
         props=rain_props, look=(0, -0.6),
         narr="Rain would bead up and ROLL off you like tiny MARBLES. You'd stay totally DRY.", n_at=4.7,
         say="Still DRY!", say_at=8.0, pitch=820, bubble_y=780),
    dict(id="ball", s=12.0, e=19.0, bg="ocean", clock="LOTUS LEAF", props=ball_props,
         narr="On a lotus leaf, a water drop stays almost a perfect BALL. Contact angle: up to 170°.",
         n_at=12.2),
    dict(id="bumps", s=19.0, e=26.0, bg="ocean", clock="ZOOM IN", props=bumps_props,
         narr="The secret: tiny BUMPS, just 10 to 20 MICROMETRES tall, coated in WAX.", n_at=19.2),
    dict(id="air", s=26.0, e=33.0, bg="ocean", clock="ZOOM IN MORE", props=air_props,
         narr="The drop sits on bump tips and AIR. Only about 0.6% of it touches the leaf.", n_at=26.2),
    dict(id="clean", s=33.0, e=40.0, bg="ocean", clock="MUDDY POND", props=clean_props,
         narr="Rolling drops grab DUST and DIRT. That's how lotus leaves stay CLEAN in muddy ponds.", n_at=33.2),
    dict(id="arbi", s=40.0, e=47.0, bg="sweetshop", clock="YOUR KITCHEN", char="kid", pos=(260, 1100, 360),
         props=arbi_props, look=(0.8, -0.3),
         narr="Your kitchen has one too: ARBI (taro) leaves bead water almost as well.", n_at=40.2,
         say="Try ONE drop!", say_at=43.4, pitch=820, bubble_y=760),
    dict(id="paint", s=47.0, e=54.0, bg="digsite", clock="COPIED BY HUMANS", props=wall_props,
         narr="Scientists COPIED it: bumpy wall paint that lets RAIN wash the dirt away.", n_at=47.2),
    dict(id="twist", s=54.0, e=62.0, bg="twist", clock="PLOT TWIST", char="samosa", pos=(540, 790, 260),
         props=samosa_props, twist=True, look=(0, 0.4),
         narr="Twist: it works for WATER, not OIL. Oily SAMOSA fingers would still leave a mark!", n_at=54.2),
    dict(id="outro", s=62.0, e=67.0),
]

def intro_extra(frame, d, T):
    if T >= 2.0:
        p = ease_back(clamp((T - 2.0) / 0.4))
        if p > 0.05:
            leaf(d, 540, 1560, int(330 * p), int(100 * p))
            drop(d, 540, 1540, int(90 * p), face=p > 0.9, T=T)

cfg = dict(
    total=67.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOUR SKIN", WHITE)], 150), 720, 0.75, "right"),
        (title([("WORKED LIKE A", WHITE)], 120), 870, 1.05, "left"),
        (title([("LOTUS LEAF?", YEL)], 170), 1030, 1.4, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" want", WHITE)], 100), 470, 0.15),
                      (title([("lotus-leaf skin?", YEL)], 96), 600, 0.45)],
               row=[("kid", 1), ("flower", 1), ("cloud", 1), ("samosa", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.5, drums=False), dict(t0=4.5, t1=33.0, melody=True),
           dict(t0=33.0, t1=47.0, melody=True), dict(t0=47.0, t1=53.85, melody=True),
           dict(t0=62.0, t1=67.0, melody=True)],
    drones=[dict(t0=54.2, dur=7.6, g=0.05)],
    fx=[("waves", 4.6, 0.15, dict(dd=6.0)), ("pop", 6.5, 0.4), ("pop", 7.6, 0.4), ("pop", 13.0, 0.5),
        ("ding", 14.4, 0.3), ("whoosh", 19.4, 0.4), ("bubbles", 26.4, 0.2, dict(dd=5.0)), ("splash", 34.2, 0.3),
        ("pop", 41.0, 0.4), ("pop", 41.5, 0.4), ("pop", 42.0, 0.4), ("splash", 48.0, 0.25), ("ding", 52.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_your_skin_worked_like_a_lotus_leaf")
