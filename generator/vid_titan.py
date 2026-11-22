#!/usr/bin/env python3
"""What if you lived on Titan? Facts: Titan is Saturn's largest moon, second-largest in the solar system (only Ganymede,
by ~2%), larger than the planet Mercury (NASA Titan facts); ~1.4 billion km (9.5 AU) from the Sun, so sunlight is
~1/90 as strong as at Earth (inverse square); surface ~-179 C (NASA); water ice as hard as granite (Planetary Society,
Howells 2024); surface pressure ~1.45-1.5 atm, ~60% more than Earth's (NASA / Planetary Society); atmosphere ~95%
nitrogen, ~5% methane (NASA); methane rain falls ~1/5 as fast as Earth rain (Planetary Society); orbit 15 d 22 h,
tidally locked, so one day ~16 Earth days (NASA); gravity 1.352 m/s^2 = 0.138 g, ~1/7 (Titan data); NASA's Dragonfly
rotorcraft launches in 2028 (NASA Titan exploration). Twist: with thick air and weak gravity a person could strap wings
on a spacesuit, flap and take off (Planetary Society 2024; Leicester students' wingsuit calc, LiveScience 2014)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 60.0
ORANGE = (232, 150, 60)
HAZE = (205, 120, 45)

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

def ball(frame, cx, cy, r, fill, bands=None, face=False, T=0.0):
    if r < 2: return
    S = int(r * 2.4)
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = S / 2
    d.ellipse([c - r - 6, c - r - 6, c + r + 6, c + r + 6], fill=OUTL)
    d.ellipse([c - r, c - r, c + r, c + r], fill=fill)
    if bands:
        for k in (-0.45, 0.05, 0.5):
            y = c + k * r
            w = math.sqrt(max(0, 1 - k * k)) * r * 0.85
            d.line([(c - w, y), (c + w, y)], fill=bands, width=max(2, int(r * 0.09)))
    if face:
        ex = r * 0.32; ey = c - r * 0.1; er = r * 0.13
        for sx in (-1, 1):
            d.ellipse([c + sx * ex - er, ey - er * 1.1, c + sx * ex + er, ey + er * 1.1], fill=WHITE, outline=OUTL,
                      width=max(2, int(r * 0.03)))
            d.ellipse([c + sx * ex - er * 0.5, ey - er * 0.4, c + sx * ex + er * 0.3, ey + er * 0.6], fill=(25, 20, 30))
        d.arc([c - r * 0.25, c + r * 0.1, c + r * 0.25, c + r * 0.4], 20, 160, fill=OUTL, width=max(2, int(r * 0.05)))
    comp(frame, L, cx - S / 2, cy - S / 2)

def titan(frame, cx, cy, r, T, face=True):
    ball(frame, cx, cy, r, ORANGE, bands=HAZE, face=face, T=T)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def surface_bg(T):
    if "surf" not in _cache:
        img = E.grad([(0, (150, 85, 35)), (0.5, (220, 145, 70)), (1, (120, 70, 35))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1330, W, H], fill=(95, 60, 35))
        rng = np.random.default_rng(7)
        for k in range(12):
            x = rng.uniform(0, W); y = rng.uniform(1370, 1900); r = rng.uniform(20, 55)
            d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=(200, 200, 205), outline=OUTL, width=3)
        d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
        _cache["surf"] = img
    img = _cache["surf"].copy(); d = ImageDraw.Draw(img)
    for k in range(4):  # drifting haze bands
        y = 520 + k * 190
        x = (k * 260 + T * 40) % 1400 - 300
        d.rounded_rectangle([x, y, x + 700, y + 40], radius=20, fill=(235, 170, 95))
    return img

# ---------------------------------------------------------------- props
def size_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = lambda t0: min(ease_back(clamp((lt - t0) / 0.5)), 1.1)
    titan(frame, 300, 1020, 200 * p(0.3), T, face=True)
    ball(frame, 780, 930, 190 * p(1.2), (165, 160, 155), bands=(135, 130, 125))
    ball(frame, 780, 1250, 135 * p(2.0), (215, 215, 220), bands=(185, 185, 195))
    if lt > 0.5: top_label(frame, "BIGGER THAN A PLANET", 380, YEL, 76)
    if lt > 1.0: at_label(frame, "TITAN", 300, 1270, ORANGE, 62)
    if lt > 1.8: at_label(frame, "MERCURY", 780, 700, WHITE, 52)
    if lt > 2.6: at_label(frame, "OUR MOON", 780, 1420, WHITE, 46)

def dist_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.4) / 2.5))
    # dim sun far left, titan far right, a dotted path between
    ball(frame, 150, 1000, 70, (255, 225, 120))
    for k in range(12):
        x = 240 + k * 50
        if x < 240 + 600 * g:
            d.ellipse([x - 7, 993, x + 7, 1007], fill=WHITE)
    titan(frame, 920, 1000, 90, T, face=True)
    if lt > 0.5: top_label(frame, "1.4 BILLION KM", 380, YEL, 96)
    if lt > 3.0: at_label(frame, "90x DIMMER SUNLIGHT", 540, 1170, WHITE, 56)

def therm(d, frac, x=840, col=(90, 170, 255)):
    d.rounded_rectangle([x - 40, 840, x + 40, 1240], radius=40, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 75, 1200, x + 75, 1350], fill=col, outline=OUTL, width=8)
    lvl = 1230 - 340 * frac
    d.rectangle([x - 20, lvl, x + 20, 1230], fill=col)
    for k in range(7):
        y = 870 + k * 50
        d.line([(x + 40, y), (x + 70, y)], fill=WHITE, width=5)

def cold_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.5) / 2.4))
    therm(d, 0.8 - 0.7 * g)
    if lt > 0.5:
        top_label(frame, f"-{int(179 * g)} °C", 380, YEL, 110)
    if lt > 3.2:
        # a rock-hard ice block
        bx, by = 150, 1330
        d.rectangle([bx - 90, by - 150, bx + 90, by], fill=(200, 230, 255), outline=OUTL, width=7)
        d.line([(bx - 50, by - 120), (bx - 10, by - 60), (bx + 30, by - 100)], fill=WHITE, width=6)
        at_label(frame, "ICE = ROCK", bx, by - 195, WHITE, 44)

def air_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, r = 800, 960, 150
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=OUTL, width=10)
    for k in range(9):
        a = math.radians(225 - k * 33.75)
        d.line([(cx + math.cos(a) * r * 0.75, cy - math.sin(a) * r * 0.75),
                (cx + math.cos(a) * r * 0.9, cy - math.sin(a) * r * 0.9)], fill=OUTL, width=6)
    g = ease_out(clamp((lt - 0.5) / 2.0))
    a = math.radians(225 - 150 * g)
    d.line([(cx, cy), (cx + math.cos(a) * r * 0.7, cy - math.sin(a) * r * 0.7)], fill=(230, 50, 40), width=10)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=OUTL)
    at_label(frame, f"{1 + 0.5 * g:.1f}x", cx, cy + r + 55, YEL, 70)
    if lt > 0.5: top_label(frame, "THICKER AIR", 380, YEL, 96)
    if lt > 3.0: top_label(frame, "95% NITROGEN", 500, WHITE, 64)

def rain_props(frame, d, T, sc):
    lt = T - sc["s"]
    # methane lake on the ground
    d.ellipse([360, 1300, 1060, 1420], fill=(60, 45, 40), outline=OUTL, width=6)
    for k in range(16):
        x = (k * 131) % 1000 + 40
        y = (k * 197 + T * 110) % 820 + 500   # slow drops
        d.ellipse([x - 12, y - 16, x + 12, y + 16], fill=(250, 200, 130), outline=OUTL, width=3)
    if lt > 0.5: top_label(frame, "METHANE RAIN", 380, YEL, 96)
    if lt > 2.5: at_label(frame, "5x SLOWER", 710, 1240, WHITE, 60)

def day_props(frame, d, T, sc):
    lt = T - sc["s"]
    x0, y0 = 120, 860
    for k in range(16):
        if lt > 0.6 + k * 0.18:
            cx = x0 + (k % 4) * 150; cy = y0 + (k // 4) * 120
            d.rounded_rectangle([cx, cy, cx + 120, cy + 95], radius=14, fill=WHITE, outline=OUTL, width=5)
            d.rectangle([cx, cy, cx + 120, cy + 26], fill=(230, 70, 60), outline=OUTL, width=5)
            if (k + 1, "n") not in _txt:
                _txt[(k + 1, "n")] = text_sprite([(str(k + 1), OUTL)], 40, stroke=0, shadow=False)
            l = _txt[(k + 1, "n")]
            comp(frame, l, cx + 60 - l.width / 2, cy + 62 - l.height / 2)
    if lt > 0.5: top_label(frame, "1 DAY = 16 EARTH DAYS", 380, YEL, 76)

def grav_props(frame, d, T, sc):
    lt = T - sc["s"]
    # bathroom scale under the kid
    d.rounded_rectangle([300, 1280, 780, 1380], radius=24, fill=WHITE, outline=OUTL, width=8)
    g = ease_out(clamp((lt - 0.8) / 2.2))
    kg = int(round(60 - 52 * g))
    d.rounded_rectangle([420, 1295, 660, 1365], radius=12, fill=(40, 50, 60))
    l = label(f"{kg} KG", 52, (120, 255, 140))
    comp(frame, l, 540 - l.width / 2, 1330 - l.height / 2)
    if lt > 0.5: top_label(frame, "GRAVITY: 1/7", 380, YEL, 100)

def drone(frame, d, cx, cy, T, s=1.0):
    # boxy rotorcraft lander with 4 rotor pairs
    d.rounded_rectangle([cx - 150 * s, cy - 50 * s, cx + 150 * s, cy + 50 * s], radius=int(20 * s),
                        fill=(230, 230, 235), outline=OUTL, width=7)
    for sx in (-1, 1):
        ax = cx + sx * 230 * s
        d.line([(cx + sx * 150 * s, cy - 20 * s), (ax, cy - 60 * s)], fill=OUTL, width=10)
        w = 110 * s * abs(math.cos(T * 30 + sx))
        d.ellipse([ax - w - 10, cy - 80 * s, ax + w + 10, cy - 60 * s], fill=(120, 130, 140), outline=OUTL, width=4)
    for sx in (-1, 1):
        d.line([(cx + sx * 90 * s, cy + 50 * s), (cx + sx * 120 * s, cy + 100 * s)], fill=OUTL, width=8)
    d.ellipse([cx - 30 * s, cy - 25 * s, cx + 30 * s, cy + 25 * s], fill=(80, 160, 230), outline=OUTL, width=5)

def drone_props(frame, d, T, sc):
    lt = T - sc["s"]
    y = 1250 - 330 * ease_out(clamp((lt - 0.5) / 3.0)) + 12 * math.sin(T * 3)
    drone(frame, d, 600, y, T, 1.0)
    if lt > 0.5: top_label(frame, "DRAGONFLY: 2028", 380, YEL, 88)

def fly_pos(T):
    lt = T - TW
    return (540, 1150 - 300 * ease_out(clamp((lt - 1.0) / 4.0)) + 20 * math.sin(T * 5), 330)

def wings(frame, d, T, sc):
    cx, cy, B = fly_pos(T)
    lt = T - sc["s"]
    cy += 8 * math.sin(T * 3.2)
    f = math.sin(T * 10) * 0.5 + 0.5   # flap
    for sx in (-1, 1):
        tip = (cx + sx * 330, cy - 150 + 220 * f)
        pts = [(cx + sx * 60, cy - 10), tip, (cx + sx * 260, cy + 80 - 40 * f), (cx + sx * 80, cy + 60)]
        d.polygon(pts, fill=(255, 255, 255), outline=OUTL, width=7)
        d.line([(cx + sx * 60, cy - 10), tip], fill=(200, 210, 230), width=6)
    if lt > 0.5: top_label(frame, "FLAP TO FLY", 380, YEL, 100)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="size", s=4.0, e=11.0, bg="space", clock="MEET TITAN", props=size_props,
         narr="Titan, Saturn's BIGGEST moon, is larger than the planet MERCURY.", n_at=4.2, narr_y=1580),
    dict(id="dist", s=11.0, e=18.0, bg="space", clock="HOW FAR?", char="kid", pos=(540, 1320, 260),
         props=dist_props, look=(0.6, -0.3),
         narr="It's about 1.4 BILLION km from the Sun. Sunlight is about 90 TIMES weaker.", n_at=11.2,
         narr_y=1580, say="Who dimmed the SUN?", say_at=14.6, pitch=440),
    dict(id="cold", s=18.0, e=25.0, bg_fn=surface_bg, clock="LANDING", char="kid", state="puff",
         pos=(480, 1120, 380), props=cold_props, look=(0.6, -0.3),
         narr="It's about -179 °C. Water ice there is as hard as ROCK.", n_at=18.2, narr_y=1580,
         say="My CHAI is a brick!", say_at=21.4, pitch=440),
    dict(id="air", s=25.0, e=32.0, bg_fn=surface_bg, clock="AIR CHECK", char="uncle", state="hat",
         pos=(330, 1120, 400), props=air_props, look=(0.6, 0),
         narr="The air is THICKER than Earth's, about 1.5 TIMES the pressure, but mostly NITROGEN.", n_at=25.2,
         narr_y=1580, say="Air, but no OXYGEN?", say_at=28.8, pitch=150),
    dict(id="rain", s=32.0, e=39.0, bg_fn=surface_bg, clock="WEATHER", char="kid", pos=(260, 1150, 340),
         props=rain_props, look=(0.4, -0.6),
         narr="It RAINS liquid methane, falling about 5 TIMES slower than our rain.", n_at=32.2, narr_y=1580,
         say="Slow-motion BAARISH!", say_at=35.4, pitch=440),
    dict(id="day", s=39.0, e=46.0, bg_fn=surface_bg, clock="CALENDAR", char="kid", pos=(870, 1240, 260),
         props=day_props, look=(-0.6, -0.4),
         narr="Titan always shows Saturn one face, so ONE DAY lasts about 16 EARTH DAYS.", n_at=39.2,
         narr_y=1580, say="16-day SUNDAY?", say_at=42.6, pitch=440),
    dict(id="grav", s=46.0, e=53.0, bg_fn=surface_bg, clock="WEIGH-IN",
         char="kid", pos=lambda T: (540, 1120 - 40 * abs(math.sin((T - 46) * 2.2)), 330), props=grav_props,
         look=(0, -0.3), narr="Gravity is only about 1/7 of Earth's. 60 KG feels like about 8 KG.", n_at=46.2,
         narr_y=1580, say="I'm a FEATHER!", say_at=49.4, pitch=440),
    dict(id="drone", s=53.0, e=TW, bg_fn=surface_bg, clock="COMING SOON", char="uncle", pos=(220, 1180, 300),
         props=drone_props, look=(0.6, -0.5),
         narr="NASA's DRAGONFLY drone is set to launch for Titan in 2028.", n_at=53.2, narr_y=1580,
         say="A FLYING robot?", say_at=56.0, pitch=150),
    dict(id="twist", s=TW, e=67.0, bg_fn=surface_bg, clock="PLOT TWIST", char="kid", pos=fly_pos,
         props=wings, twist=True, look=(0, -0.3),
         narr="Twist: thick air plus weak gravity. Strap WINGS on your suit, flap, and you could FLY.",
         n_at=TW + 0.2, narr_y=1580, say="I'm FLYING!", say_at=TW + 3.8, pitch=440),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        titan(frame, 540, 1390 + 12 * math.sin(T * 2), 170 * p, T, face=True)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED ON", WHITE)], 120), 770, 0.75, "right"),
        (title([("TITAN?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" fly", WHITE)], 100), 470, 0.15),
                      (title([("on Titan?", YEL)], 96), 600, 0.45)],
               row=[("rocket", 1), ("earth", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, drums=False, melody=True),
           dict(t0=18.0, t1=32.0, minor=True), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=18.0, dur=14.0, g=0.22)],
    fx=[("whoosh", 5.0, 0.3), ("pop", 5.4, 0.3), ("pop", 6.2, 0.3), ("pop", 7.0, 0.3),
        ("wind", 18.4, 0.25, dict(dd=5.0)), ("crash", 21.4, 0.2), ("tick", 26.0, 0.3),
        ("bubbles", 32.4, 0.2, dict(dd=5.0)), ("tick", 40.0, 0.3), ("tick", 41.0, 0.3), ("tick", 42.0, 0.3),
        ("ding", 49.0, 0.25), ("rumble", 53.6, 0.3, dict(dd=3.0)), ("wind", TW + 0.5, 0.25, dict(dd=6.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_on_titan")
