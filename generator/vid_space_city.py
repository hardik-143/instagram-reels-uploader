#!/usr/bin/env python3
"""What if you lived in a spinning space city? Facts: astronauts' bones lose 1-1.5% of their density each month on
4-6 month missions (NASA, Risk of Spaceflight-Induced Bone Changes). Gerard K. O'Neill first published the design in
Physics Today, Sept 1974, then 'The High Frontier' (1976); Island Three cylinders are 6.4 or 8.0 km in diameter
(sources differ) and 32 km long, with three land stripes and three window stripes plus hinged mirrors that reflect
sunlight in and can simulate night; dropped objects would drift a few centimetres from Coriolis effects (Wikipedia:
O'Neill cylinder). Spin maths: for 1 g at r = 3.2-4 km, period = 2*pi*sqrt(r/g) = 113-127 s (~2 min, ~28 turns per
hour as Wikipedia says), rim speed = 640-713 km/h ('over 600 km/h'). Spin gravity scales with distance from the axis,
so it falls to zero at the centre. Bandra-Worli Sea Link is 5.6 km (Wikipedia) -> 32 km is almost 6x. Bharatiya
Antariksh Station: first module BAS-01 approved for launch by 2028, full station by 2035 (PIB parliament answer, July
2026). Twist: Earth's equator moves ~1,670 km/h; centripetal effect = omega^2 R = 0.034 m/s^2 = ~0.35% of g, so you
are only about 0.3% lighter."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 60.0
GREEN = (110, 190, 100)
GREEN_D = (70, 140, 70)
GLASS = (120, 190, 245)
METAL = (200, 206, 220)
METAL_D = (150, 156, 176)

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

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0, rot=0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    if rot: spr = spr.rotate(rot, resample=Image.BICUBIC, expand=False)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- drawings
def cylinder(d, cx, cy, Lh, R, ang):
    """Side view of a spinning cylinder (axis horizontal). Lh = half length."""
    if Lh < 60 or R < 40: return
    d.rounded_rectangle([cx - Lh, cy - R, cx + Lh, cy + R], radius=30, fill=METAL_D, outline=OUTL, width=7)
    for k in range(6):
        th = ang + k * math.pi / 3
        a0, a1 = th - math.pi / 6, th + math.pi / 6
        if math.cos(th) <= 0: continue
        y0, y1 = cy + R * math.sin(max(a0, -math.pi / 2)), cy + R * math.sin(min(a1, math.pi / 2))
        if y1 - y0 < 2: continue
        col = GREEN if k % 2 == 0 else GLASS
        d.rectangle([cx - Lh + 20, y0, cx + Lh - 20, y1], fill=col)
        if k % 2 == 0:
            for j in range(8):
                x = cx - Lh + 60 + j * (2 * Lh - 120) / 7
                d.rectangle([x - 8, (y0 + y1) / 2 - 6, x + 8, (y0 + y1) / 2 + 6], fill=(240, 240, 240))
    d.rounded_rectangle([cx - Lh, cy - R, cx + Lh, cy + R], radius=30, outline=OUTL, width=7)
    for sx in (-1, 1):
        d.ellipse([cx + sx * Lh - 26, cy - R, cx + sx * Lh + 26, cy + R], fill=METAL, outline=OUTL, width=6)

def ring(frame, d, cx, cy, R, ang, T, houses=True, kid_on=True, kid_r=None, kid_size=120):
    """Cross-section of the habitat: a ring whose inside is the ground. ang = current rotation (rad)."""
    d.ellipse([cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40], fill=METAL_D, outline=OUTL, width=7)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(150, 210, 250), outline=OUTL, width=6)
    # ground band (land) as thick arc segments, alternating with windows
    for k in range(6):
        a0 = math.degrees(ang) + k * 60
        if k % 2 == 0:
            d.arc([cx - R, cy - R, cx + R, cy + R], a0, a0 + 60, fill=GREEN, width=46)
        else:
            d.arc([cx - R, cy - R, cx + R, cy + R], a0, a0 + 60, fill=(250, 240, 160), width=20)
    d.ellipse([cx - R + 46, cy - R + 46, cx + R - 46, cy + R - 46], outline=OUTL, width=3)
    if houses:
        for k in range(3):
            for j in range(4):
                a = ang + math.radians(k * 120 + 12 + j * 12)
                hx = cx + (R - 60) * math.cos(a); hy = cy + (R - 60) * math.sin(a)
                # house as rotated square pointing to centre
                ux, uy = -math.cos(a), -math.sin(a)          # "up" points to the centre
                vx, vy = -uy, ux
                s = 22
                pts = [(hx + vx * s - ux * 0, hy + vy * s - uy * 0), (hx - vx * s, hy - vy * s),
                       (hx - vx * s + ux * 2 * s, hy - vy * s + uy * 2 * s), (hx + ux * 3 * s, hy + uy * 3 * s),
                       (hx + vx * s + ux * 2 * s, hy + vy * s + uy * 2 * s)]
                d.polygon(pts, fill=(250, 210, 150) if j % 2 else (240, 140, 120), outline=OUTL)
    if kid_on:
        a = ang + math.radians(90)
        r = kid_r if kid_r is not None else R - 46 - kid_size * 0.45
        kx = cx + r * math.cos(a); ky = cy + r * math.sin(a)
        rot = -math.degrees(a) + 90
        mini(frame, "kid", kx, ky, kid_size, T, look=(0, -0.3), rot=rot)

# ---------------------------------------------------------------- props
def float_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "kid", 540 + 60 * math.sin(T * 0.7), 960 + 40 * math.sin(T * 1.1), 300, T, look=(0.3, 0.2),
         rot=25 * math.sin(T * 0.9) + lt * 20)
    m = int(clamp((lt - 1.0) / 4.0) * 6)
    put(frame, f"MONTH {m}", 270, 1240, 64, WHITE)
    put(frame, f"-{m * 1.5:.0f}% BONE", 780, 1240, 64, YEL)
    if lt > 0.5: top_label(frame, "ZERO-G PROBLEM", 380, YEL, 92)

def spin_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    cylinder(d, 540, 980, 420 * p + 2, 150 * p + 2, T * 1.2)
    # spin arrow
    if lt > 0.8:
        d.arc([60, 780, 200, 1180], 100, 260, fill=YEL, width=10)
        d.polygon([(118, 770), (150, 800), (110, 818)], fill=YEL, outline=OUTL)
    if lt > 0.5: top_label(frame, "SPIN IT!", 380, YEL, 110)

def size_props(frame, d, T, sc):
    lt = T - sc["s"]
    cylinder(d, 540, 760, 460, 70, T * 1.2)
    put(frame, "32 KM", 540, 860, 80, YEL)
    n = int(clamp((lt - 1.0) / 3.5) * 6)
    seg = 920 / 32 * 5.6
    for k in range(n):
        x0 = 80 + k * seg
        d.rectangle([x0 + 4, 1060, x0 + seg - 4, 1084], fill=(230, 230, 240), outline=OUTL, width=4)
        d.line([(x0 + seg / 2, 1060), (x0 + seg / 2 - 30, 1010)], fill=OUTL, width=5)
        d.line([(x0 + seg / 2, 1060), (x0 + seg / 2 + 30, 1010)], fill=OUTL, width=5)
        d.rectangle([x0 + seg / 2 - 6, 1000, x0 + seg / 2 + 6, 1062], fill=(240, 240, 250), outline=OUTL, width=3)
    if n: put(frame, "ALMOST 6 SEA LINKS" if n == 6 else f"{n} SEA LINKS", 540, 1120, 64, WHITE)
    if lt > 0.5: top_label(frame, "6-8 KM WIDE", 380, YEL, 96)

def gravity_props(frame, d, T, sc):
    lt = T - sc["s"]
    ring(frame, d, 540, 1010, 350, T * 0.6, T)
    put(frame, "FLOOR: 600+ KM/H", 540, 492, 52, WHITE)
    if lt > 0.5: top_label(frame, "1 TURN = ~2 MIN", 380, YEL, 92)

def sky_props(frame, d, T, sc):
    lt = T - sc["s"]
    ring(frame, d, 540, 980, 360, 0.0, T)
    # arrow from kid up to the far houses
    if lt > 1.0:
        y = 1240 - 520 * clamp((lt - 1.0) / 1.2)
        d.line([(540, 1240), (540, y)], fill=YEL, width=10)
        if y < 760:
            d.polygon([(520, y + 20), (560, y + 20), (540, y - 14)], fill=YEL, outline=OUTL)
    if lt > 0.5: top_label(frame, "HOUSES OVERHEAD", 380, YEL, 88)

def climb_props(frame, d, T, sc):
    lt = T - sc["s"]
    R = 360
    c = clamp((lt - 1.0) / 4.0)
    r = (R - 46 - 54) * (1 - c)
    ring(frame, d, 540, 980, R, 0.0, T, kid_on=True, kid_r=r, kid_size=120)
    d.line([(540, 980), (540, 980 + R - 40)], fill=OUTL, width=6)
    put(frame, f"WEIGHT {int(round((1 - c) * 100))}%", 760, 930, 56, WHITE if c < 0.99 else YEL)
    if lt > 0.5: top_label(frame, "CLIMB TO THE MIDDLE", 380, YEL, 80)

def ladoo_props(frame, d, T, sc):
    lt = T - sc["s"]
    gy = 1260
    d.rectangle([0, gy, W, gy + 160], fill=GREEN, outline=OUTL, width=6)
    # tower
    d.rectangle([380, 640, 470, gy], fill=(230, 220, 200), outline=OUTL, width=6)
    for k in range(5):
        d.rectangle([400, 680 + k * 110, 450, 730 + k * 110], fill=GLASS, outline=OUTL, width=3)
    # target
    tx = 510
    for r, col in ((70, (230, 60, 60)), (46, WHITE), (22, (230, 60, 60))):
        d.ellipse([tx - r, gy - 14 - r * 0.25, tx + r, gy - 14 + r * 0.25], fill=col, outline=OUTL, width=3)
    f = clamp((lt - 1.0) / 1.6)
    lx = 510 + 70 * f * f
    ly = 640 + (gy - 60 - 640) * f * f
    mini(frame, "ladoo", lx, ly, 100, T)
    if f >= 1: put(frame, "OFF TARGET!", 760, 1120, 60, YEL)
    if lt > 0.5: top_label(frame, "SPIN BENDS FALLS", 380, YEL, 90)

def module(d, x, y, w, h, col=METAL):
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=h / 2, fill=col, outline=OUTL, width=6)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = 1 + int(clamp((lt - 1.5) / 3.5) * 4)
    xs = [540, 340, 740, 540, 540]
    ys = [960, 960, 960, 800, 1120]
    for k in range(n):
        if k in (1, 2):
            module(d, xs[k], ys[k], 200, 110)
        elif k in (3, 4):
            module(d, xs[k], ys[k], 110, 160)
        else:
            module(d, xs[k], ys[k], 220, 130, (240, 240, 250))
            d.rectangle([xs[k] - 10, ys[k] - 40, xs[k] + 10, ys[k] + 40], fill=(255, 153, 51))
    for sx in (-1, 1):
        d.rectangle([540 + sx * 450 - 60, 900, 540 + sx * 450 + 60, 1020], fill=(60, 80, 160), outline=OUTL, width=5)
    put(frame, f"{n} OF 5 MODULES", 540, 1250, 64, WHITE)
    if lt > 0.5: top_label(frame, "2028 -> 2035".replace("->", "TO"), 380, YEL, 96)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "earth", 540, 960, 460, T, state=T * 0.3, look=(0, 0.2))
    d.arc([260, 680, 820, 1240], 200, 340, fill=YEL, width=10)
    put(frame, "1,670 KM/H", 540, 1260, 80, YEL)
    if lt > 0.5: top_label(frame, "EARTH SPINS TOO", 380, YEL, 92)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="float", s=4.0, e=11.0, bg="space", clock="IN ORBIT", props=float_props,
         narr="In space you FLOAT, and astronauts lose about 1-1.5% of their bone density every MONTH.",
         n_at=4.2, narr_y=1580),
    dict(id="spin", s=11.0, e=18.0, bg="space", clock="1974", props=spin_props,
         narr="The fix? SPIN! In 1974 physicist Gerard O'NEILL designed giant spinning space cities.",
         n_at=11.2, narr_y=1580),
    dict(id="size", s=18.0, e=25.0, bg="space", clock="ISLAND THREE", props=size_props,
         narr="His biggest: a tube about 32 KM long, almost 6 BANDRA-WORLI Sea Links end to end.",
         n_at=18.2, narr_y=1580),
    dict(id="gravity", s=25.0, e=32.0, bg="space", clock="FAKE GRAVITY", props=gravity_props,
         narr="One turn every ~2 MINUTES pushes you onto the floor with Earth-like gravity.", n_at=25.2,
         narr_y=1580),
    dict(id="sky", s=32.0, e=39.0, bg="space", clock="LOOK UP", props=sky_props,
         narr="Look UP and you'd see houses on the 'ceiling', kilometres away. Giant MIRRORS bring in sunlight.",
         n_at=32.2, narr_y=1580),
    dict(id="climb", s=39.0, e=46.0, bg="space", clock="CLIMB", props=climb_props,
         narr="Climb toward the middle and you get LIGHTER. At the very centre: ZERO gravity.", n_at=39.2,
         narr_y=1580),
    dict(id="ladoo", s=46.0, e=53.0, bg="day", clock="WEIRD BIT", props=ladoo_props, char="kid",
         pos=(220, 1150, 220), look=(0.6, -0.3),
         narr="Spin also bends falling things: drop a LADOO from a tower and it lands slightly off target.",
         n_at=46.2, narr_y=1580, say="My LADOO missed!", say_at=50.0, pitch=440),
    dict(id="india", s=53.0, e=TW, bg="space", clock="INDIA", props=india_props,
         narr="India's BHARATIYA ANTARIKSH STATION: first module by 2028, full by 2035. No spin, so you FLOAT.",
         n_at=53.2, narr_y=1580),
    dict(id="twist", s=TW, e=67.0, bg="space", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: Earth's equator spins at 1,670 KM/H, yet that makes you only about 0.3% LIGHTER.",
         n_at=TW + 0.2, narr_y=1600),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.1)
        cylinder(d, 540, 1380, 380 * p + 2, 110 * p + 2, T * 1.2)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU LIVED IN A", WHITE)], 120), 730, 0.75, "right"),
        (title([("SPINNING SPACE CITY?", YEL)], 110), 870, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" move", WHITE)], 100), 470, 0.15),
                      (title([("to a space city?", YEL)], 100), 600, 0.45)],
               row=[("kid", 1), ("rocket", 1), ("earth", 1), ("moon", 1), ("ladoo", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=4.0, dur=7.0, g=0.12)],
    fx=[("whoosh", 11.6, 0.4), ("rumble", 12.0, 0.15, dict(dd=4.0)), ("pop", 19.5, 0.2), ("pop", 20.1, 0.2),
        ("pop", 20.7, 0.2), ("pop", 21.3, 0.2), ("pop", 21.9, 0.2), ("pop", 22.5, 0.2),
        ("whoosh", 33.2, 0.3), ("whoosh", 47.0, 0.3), ("click", 48.6, 0.4), ("pop", 55.0, 0.2),
        ("pop", 56.0, 0.2), ("pop", 57.0, 0.2), ("pop", 58.0, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_in_a_spinning_space_city")
