#!/usr/bin/env python3
"""What if you fired a cannon from Everest? Newton's cannonball thought experiment: a cannon on a very high mountain,
no air resistance; slow shots fall back, at orbital speed the ball circles Earth, above escape speed it leaves
(Newton, Principia 1687 / A Treatise of the System of the World). Everest height 8,849 m (2020 China-Nepal survey).
Fall time from 8,849 m with no air: sqrt(2h/g) = ~42.5 s, so a 1 km/s shot lands ~42 km away (curvature adds only
~0.1 km). A horizontally launched projectile falls ~5 m in its first second; Earth's surface curves ~5 m down for every
8,000 m, so ~8 km/s near the surface keeps pace with the curve (The Physics Classroom, 'Satellite Motion'). Circular
orbital speed at sea level ~7.9 km/s, escape speed ~11.2 km/s (Engineering ToolBox, 'Satellites - Orbital Velocity');
7.9 km/s = ~28,400 km/h. Orbit period at r = 6,380 km: 2*pi*sqrt(r^3/GM) = ~5,070 s = ~84 min. The ISS and satellites
are in continuous free fall around Earth (NASA). Twist: after ~84 min the ball returns to the cannon from behind."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 60.0
ROCK = (120, 110, 130)
SNOW = (246, 248, 255)
BALL = (40, 40, 52)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def put(frame, txt, cx, y, size=52, col=WHITE):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2)):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, 0, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def sky_bg():
    """Dark-blue high sky with a big curved Earth at the bottom (centre far below the frame)."""
    if "sky" not in _bgc:
        img = grad([(0, (16, 24, 60)), (0.55, (40, 80, 150)), (1, (90, 150, 210))], W, H)
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(4)
        for k in range(50):
            x = rng.uniform(0, W); y = rng.uniform(0, 700); r = rng.uniform(1.5, 3.5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 230, 255))
        R = 2600; cy = 1330 + R
        d.ellipse([540 - R - 30, cy - R - 30, 540 + R + 30, cy + R + 30], fill=(150, 200, 250))
        d.ellipse([540 - R, cy - R, 540 + R, cy + R], fill=(70, 150, 90), outline=OUTL, width=6)
        d.ellipse([540 - R + 60, cy - R + 60, 540 + R - 60, cy + R - 60], fill=(56, 120, 76))
        _bgc["sky"] = img
    return _bgc["sky"]

def ground_y(x):
    R = 2600; cy = 1330 + R
    return cy - math.sqrt(max(0, R * R - (x - 540) ** 2))

def space_bg():
    if "space" not in _bgc:
        img = grad([(0, (10, 10, 30)), (1, (24, 20, 60))], W, H)
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(8)
        for k in range(120):
            x = rng.uniform(0, W); y = rng.uniform(0, H); r = rng.uniform(1, 3)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 220, 255))
        _bgc["space"] = img
    return _bgc["space"]

# ---------------------------------------------------------------- drawing helpers
def mountain(d, cx, base_y, h, w):
    d.polygon([(cx - w, base_y), (cx, base_y - h), (cx + w, base_y)], fill=ROCK, outline=OUTL)
    d.line([(cx - w, base_y), (cx, base_y - h), (cx + w, base_y)], fill=OUTL, width=6)
    sw = w * 0.32
    d.polygon([(cx - sw, base_y - h + h * 0.32), (cx, base_y - h), (cx + sw, base_y - h + h * 0.32),
               (cx + sw * 0.4, base_y - h + h * 0.24), (cx, base_y - h + h * 0.34),
               (cx - sw * 0.4, base_y - h + h * 0.24)], fill=SNOW, outline=OUTL)

def cannon(d, x, y, s=1.0, recoil=0.0):
    x = x - 20 * s * recoil
    d.rounded_rectangle([x - 60 * s, y - 34 * s, x + 70 * s, y], radius=10 * s, fill=(70, 70, 86), outline=OUTL,
                        width=max(2, int(5 * s)))
    d.ellipse([x + 60 * s, y - 38 * s, x + 80 * s, y + 4 * s], fill=(40, 40, 52), outline=OUTL, width=3)
    for wx in (-40, 20):
        r = 22 * s
        d.ellipse([x + wx * s - r, y - r * 0.3, x + wx * s + r, y + r * 1.7], fill=(150, 100, 60), outline=OUTL,
                  width=max(2, int(4 * s)))

def ball(d, x, y, r=16):
    d.ellipse([x - r, y - r, x + r, y + r], fill=BALL, outline=WHITE, width=3)

def dashed(d, pts, col=WHITE, w=5, on=3):
    for i in range(0, len(pts) - 1):
        if (i // on) % 2 == 0:
            d.line([pts[i], pts[i + 1]], fill=col, width=w)

def peak():
    return 540, 1330 - 430   # summit position in sky scenes

def mountain_scene(d):
    mountain(d, 540, 1340, 430, 330)

def iss(d, x, y, s=1.0):
    d.rectangle([x - 130 * s, y - 8 * s, x + 130 * s, y + 8 * s], fill=(190, 190, 200), outline=OUTL, width=3)
    for dx in (-110, -70, 70, 110):
        d.rectangle([x + (dx - 16) * s, y - 70 * s, x + (dx + 16) * s, y + 70 * s], fill=(60, 90, 170),
                    outline=OUTL, width=3)
    d.rounded_rectangle([x - 40 * s, y - 20 * s, x + 40 * s, y + 20 * s], radius=10 * s, fill=WHITE, outline=OUTL,
                        width=3)

# ---------------------------------------------------------------- props
def newton_props(frame, d, T, sc):
    lt = T - sc["s"]
    mountain_scene(d)
    px, py = peak()
    cannon(d, px - 10, py + 4, 1.5)
    if lt > 2.5:
        q = clamp((lt - 2.5) / 1.4)
        x = px + 80 + 520 * q
        ball(d, x, py - 18)
        dashed(d, [(px + 80 + 520 * q * i / 20, py - 18) for i in range(21)], w=4)
    if lt > 0.5: top_label(frame, "NEWTON'S CANNON", 380, YEL, 96)
    if lt > 1.2: put(frame, "a thought experiment", 540, 500, 54, WHITE)

def everest_props(frame, d, T, sc):
    lt = T - sc["s"]
    mountain_scene(d)
    px, py = peak()
    cannon(d, px - 10, py + 4, 1.5)
    # height arrow drawn as a bar with ticks
    d.line([(930, py), (930, 1300)], fill=WHITE, width=6)
    for y in (py, 1300):
        d.line([(900, y), (960, y)], fill=WHITE, width=6)
    if lt > 1.0: put(frame, "8,849 M", 900, (py + 1300) / 2 - 30, 60, YEL)
    if lt > 3.0: put(frame, "NO AIR (PRETEND)", 540, 560, 64, WHITE)
    if lt > 0.5: top_label(frame, "MOUNT EVEREST", 380, YEL, 100)

def slow_props(frame, d, T, sc):
    lt = T - sc["s"]
    mountain_scene(d)
    px, py = peak()
    q = clamp((lt - 0.8) / 3.0)
    cannon(d, px - 10, py + 4, 1.5, recoil=max(0, 1 - (lt - 0.8) * 4) if lt > 0.8 else 0)
    pts = []
    for i in range(31):
        t = q * i / 30
        x = px + 100 + 230 * t
        y = py - 18 + (ground_y(px + 330) - (py - 18)) * t * t
        pts.append((x, y))
    if lt > 0.8:
        dashed(d, pts, w=4)
        ball(d, *pts[-1])
    if q >= 1:
        put(frame, "THUD!", pts[-1][0], pts[-1][1] - 120, 60, YEL)
    if lt > 1.0:
        t_s = int(round(42 * q))
        put(frame, f"{t_s} S IN THE AIR", 540, 520, 64, WHITE)
    if lt > 0.5: top_label(frame, "1 KM/S", 380, YEL, 110)

def fall_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 1.0) / 2.5)
    # two shelves, slow ball and fast ball both fall the same
    y0 = 700
    for k, (lab, vx) in enumerate([("SLOW", 120), ("FAST", 480)]):
        x0 = 140
        x = x0 + vx * q
        y = y0 + k * 360 + 200 * q * q
        d.line([(x0 - 60, y0 + k * 360 + 18), (x0 + 30, y0 + k * 360 + 18)], fill=WHITE, width=8)
        trail = [(x0 + vx * q * i / 20, y0 + k * 360 + 200 * (q * i / 20) ** 2) for i in range(21)]
        dashed(d, trail, w=4)
        ball(d, x, y, 30)
        put(frame, lab, x0 - 10, y0 + k * 360 - 90, 60, WHITE)
        if q >= 1:
            d.line([(x + 60, y0 + k * 360), (x + 60, y0 + k * 360 + 200)], fill=YEL, width=6)
            put(frame, "5 M", x + 130, y0 + k * 360 + 70, 56, YEL)
    if lt > 0.5: top_label(frame, "SAME DROP: 1 SECOND", 380, YEL, 84)

def curve_props(frame, d, T, sc):
    lt = T - sc["s"]
    # straight line vs curved surface
    R = 1900; cx = 540; cy = 900 + R
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(70, 150, 90), outline=OUTL, width=6)
    q = clamp((lt - 0.8) / 2.0)
    x1 = 120 + 840 * q
    d.line([(120, 900), (x1, 900)], fill=WHITE, width=6)
    if q >= 1:
        gy = cy - math.sqrt(R * R - (960 - cx) ** 2)
        d.line([(960, 900), (960, gy)], fill=YEL, width=8)
        put(frame, "5 M", 960, 760, 60, YEL)
        put(frame, "8 KM", 540, 820, 60, WHITE)
    if lt > 0.5: top_label(frame, "EARTH CURVES AWAY", 380, YEL, 90)

def orbit_props(frame, d, T, sc, label_txt="7.9 KM/S"):
    lt = T - sc["s"]
    cx, cy, R = 540, 1000, 290
    mini(frame, "earth", cx, cy, 2 * R, T, state=T * 0.1)
    # tiny mountain + cannon on top
    a = -math.pi / 2 + max(0, lt - 0.6) * 1.2
    rr = R + 80
    pts = [(cx + rr * math.cos(-math.pi / 2 + t * (a + math.pi / 2) / 40),
            cy + rr * math.sin(-math.pi / 2 + t * (a + math.pi / 2) / 40)) for t in range(41)]
    dashed(d, pts, w=4)
    ball(d, cx + rr * math.cos(a), cy + rr * math.sin(a), 24)
    if lt > 2.0: put(frame, "FALLING... AND MISSING", 540, 510, 58, WHITE)
    if lt > 0.5: top_label(frame, label_txt, 380, YEL, 110)

def iss_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, R = 540, 1000, 290
    mini(frame, "earth", cx, cy, 2 * R, T, state=T * 0.1)
    for k, (rr, sp, off) in enumerate([(330, 1.1, 0), (380, 0.8, 2.0), (430, 0.6, 4.0)]):
        a = off + lt * sp
        x = cx + rr * math.cos(a); y = cy + rr * 0.9 * math.sin(a)
        if k == 0:
            iss(d, x, y, 0.45)
        else:
            d.rectangle([x - 14, y - 10, x + 14, y + 10], fill=(220, 220, 230), outline=OUTL, width=3)
            d.rectangle([x - 44, y - 6, x - 16, y + 6], fill=(60, 90, 170), outline=OUTL, width=2)
            d.rectangle([x + 16, y - 6, x + 44, y + 6], fill=(60, 90, 170), outline=OUTL, width=2)
    if lt > 1.5: put(frame, "ALWAYS FALLING", 540, 510, 62, WHITE)
    if lt > 0.5: top_label(frame, "THAT'S AN ORBIT", 380, YEL, 100)

def escape_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 0.6) / 5.0)
    s = 500 * (1 - 0.7 * ease_out(q))
    cx, cy = 300 - 120 * q, 1150 + 120 * q
    mini(frame, "earth", cx, cy, s, T, state=T * 0.1)
    bx = cx + 40 + 760 * ease_out(q); by = cy - s / 2 - 40 - 520 * q
    pts = [(cx + 40 + 760 * ease_out(q * i / 30), cy - s / 2 - 40 - 520 * q * i / 30) for i in range(31)]
    dashed(d, pts, w=4)
    ball(d, bx, by, 24)
    if lt > 2.5: put(frame, "BYE, EARTH!", 540, 510, 64, WHITE)
    if lt > 0.5: top_label(frame, "11.2 KM/S", 380, YEL, 110)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    mountain_scene(d)
    px, py = peak()
    cannon(d, px - 10, py + 4, 1.5)
    # ball comes in from the left, from behind the cannon
    q = clamp((lt - 1.2) / 1.6)
    bx = -40 + (px - 110 + 40) * q
    ball(d, bx, py - 18, 18)
    dashed(d, [(-40 + (bx + 40) * i / 20, py - 18) for i in range(21)], w=4)
    if q >= 1:
        put(frame, "CLANG!", px - 230, py + 60, 80, YEL)
    if lt > 0.3: top_label(frame, "84 MINUTES LATER", 380, YEL, 92)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="newton", s=4.0, e=11.0, bg_fn=lambda T: sky_bg(), clock="1687", props=newton_props,
         narr="Isaac NEWTON imagined a cannon on a huge mountain, firing SIDEWAYS.", n_at=4.2, narr_y=1580),
    dict(id="everest", s=11.0, e=18.0, bg_fn=lambda T: sky_bg(), clock="8,849 M", props=everest_props,
         narr="Put it on EVEREST, 8,849 M up, and pretend there's NO AIR to slow the ball.", n_at=11.2,
         narr_y=1580),
    dict(id="slow", s=18.0, e=25.0, bg_fn=lambda T: sky_bg(), clock="SHOT 1", props=slow_props,
         narr="Fire at 1 KM/S: the ball falls for about 42 SECONDS and lands about 42 KM away.", n_at=18.2,
         narr_y=1580),
    dict(id="fall", s=25.0, e=32.0, bg_fn=lambda T: space_bg(), clock="RULE 1", props=fall_props,
         narr="Slow or fast, every ball DROPS about 5 METRES in its first second.", n_at=25.2, narr_y=1580),
    dict(id="curve", s=32.0, e=39.0, bg_fn=lambda T: space_bg(), clock="RULE 2", props=curve_props,
         narr="And Earth's surface curves DOWN about 5 METRES for every 8 KM.", n_at=32.2, narr_y=1580),
    dict(id="orbit", s=39.0, e=46.0, bg_fn=lambda T: space_bg(), clock="SHOT 2", props=orbit_props,
         narr="So fire at about 7.9 KM/S, over 28,000 KM/H. The ground curves away as fast as it falls!",
         n_at=39.2, narr_y=1580),
    dict(id="iss", s=46.0, e=53.0, bg_fn=lambda T: space_bg(), clock="ORBIT", props=iss_props,
         narr="That's how the ISS and every SATELLITE stay up: they're always FALLING around Earth.",
         n_at=46.2, narr_y=1580),
    dict(id="escape", s=53.0, e=TW, bg_fn=lambda T: space_bg(), clock="SHOT 3", props=escape_props,
         narr="Fire at 11.2 KM/S and the ball ESCAPES Earth and never comes back.", n_at=53.2, narr_y=1580),
    dict(id="twist", s=TW, e=67.0, bg_fn=lambda T: sky_bg(), clock="PLOT TWIST", props=twist_props,
         char="kid", pos=(830, 1180, 240), look=(-0.7, -0.3), twist=True,
         narr="Twist: fire at orbit speed and about 84 MINUTES later the ball hits your cannon from BEHIND!",
         n_at=TW + 0.2, narr_y=1600, say="It came BACK?!", say_at=TW + 3.2, pitch=440),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        d2 = ImageDraw.Draw(frame)
        mountain(d2, 540, 1500, 360 * p, 300 * p)
        if p > 0.9:
            cannon(d2, 530, 1500 - 360 * p + 6, 0.9)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 470, 0.2, "pop"),
        (title([("YOU FIRED A CANNON", WHITE)], 96), 680, 0.75, "right"),
        (title([("FROM EVEREST?", YEL)], 140), 800, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("If ", WHITE), ("YOU", YEL), (" had Newton's cannon,", WHITE)], 80), 470, 0.15),
                      (title([("which speed would you pick?", YEL)], 76), 590, 0.45)],
               row=[("kid", 1), ("earth", 1), ("rocket", 1), ("moon", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("boom", 6.5, 0.3), ("wind", 11.2, 0.12, dict(dd=6.0)), ("boom", 18.8, 0.35), ("crash", 21.8, 0.25),
        ("whoosh", 26.0, 0.3), ("ding", 34.8, 0.2), ("boom", 39.6, 0.3), ("whoosh", 47.0, 0.3),
        ("boom", 53.6, 0.3), ("whoosh", 55.0, 0.4), ("crash", TW + 2.8, 0.35)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_fired_a_cannon_from_everest")
