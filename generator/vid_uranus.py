#!/usr/bin/env python3
"""What if you lived on Uranus? NASA facts: about 2.9 billion km from the Sun, sunlight takes 2 h 40 min; axial tilt
97.77 deg, so it spins on its side; ~17 h day; year ~84 Earth years (30,687 days); no true surface, mostly a hot dense
fluid of 'icy' water, methane and ammonia; minimum atmospheric temperature 49 K (-224 C), colder than Neptune in places;
winds up to 900 km/h (science.nasa.gov/uranus/facts, NSSDC fact sheet). Each pole gets about 42 years of sunlight, then
42 years of darkness (NASA JPL Night Sky Network). Airliner cruise ~900 km/h. India life expectancy at birth ~72 years
(World Bank 2024 via FRED). Twist: hydrogen sulfide detected above the cloud tops with Gemini North, so Uranus would smell
like rotten eggs, but you'd freeze/suffocate first (Irwin et al., Nature Astronomy, April 2018; Space.com)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
CYAN = (150, 225, 235)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0, rot=0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    if rot: spr = spr.rotate(rot, resample=Image.BICUBIC, expand=False)
    comp(frame, spr, x - size / 2, y - size / 2)

def uranus(frame, cx, cy, r, T, tilt=98.0, face=True):
    """Pale cyan ice giant with faint bands and a thin ring system, tipped on its side."""
    S = int(r * 3.2)
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = S / 2
    # ring, back half
    ring = [c - r * 1.45, c - r * 0.42, c + r * 1.45, c + r * 0.42]
    d.arc(ring, 180, 360, fill=(220, 240, 245), width=max(2, int(r * 0.05)))
    d.ellipse([c - r - 6, c - r - 6, c + r + 6, c + r + 6], fill=OUTL)
    d.ellipse([c - r, c - r, c + r, c + r], fill=CYAN)
    for k in (-0.5, 0.0, 0.5):
        y = c + k * r
        w = math.sqrt(max(0, 1 - k * k)) * r
        d.line([(c - w * 0.95, y), (c + w * 0.95, y)], fill=(130, 205, 220), width=max(2, int(r * 0.08)))
    d.arc(ring, 0, 180, fill=(220, 240, 245), width=max(2, int(r * 0.05)))
    L = L.rotate(tilt - 90 + 90, resample=Image.BICUBIC, expand=False) if tilt else L
    if face:
        fd = ImageDraw.Draw(L)
        ex = r * 0.32; ey = c - r * 0.1; er = r * 0.13
        for sx in (-1, 1):
            fd.ellipse([c + sx * ex - er, ey - er * 1.1, c + sx * ex + er, ey + er * 1.1], fill=WHITE, outline=OUTL,
                       width=max(2, int(r * 0.03)))
            fd.ellipse([c + sx * ex - er * 0.5, ey - er * 0.4, c + sx * ex + er * 0.3, ey + er * 0.6], fill=(25, 20, 30))
        fd.arc([c - r * 0.25, c + r * 0.1, c + r * 0.25, c + r * 0.4], 20, 160, fill=OUTL, width=max(2, int(r * 0.05)))
    comp(frame, L, cx - S / 2, cy - S / 2)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def clouds_bg(T):
    if "clouds" not in _cache:
        img = E.grad([(0, (110, 190, 210)), (0.6, (160, 225, 235)), (1, (60, 120, 160))], W, H).convert("RGBA")
        _cache["clouds"] = img
    img = _cache["clouds"].copy(); d = ImageDraw.Draw(img)
    for k in range(9):
        y = (k * 260 - T * 420) % 2300 - 200
        x = 120 + (k * 397) % 840
        for dx, r in ((-90, 70), (0, 100), (90, 70)):
            d.ellipse([x + dx - r, y - r * 0.6, x + dx + r, y + r * 0.6], fill=(200, 240, 245))
    return img

def dark_bg(T):
    if "dark" not in _cache:
        img = E.grad([(0, (6, 10, 30)), (1, (20, 30, 60))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img); rng = np.random.default_rng(3)
        for k in range(120):
            x, y = rng.uniform(0, W), rng.uniform(0, H); r = rng.uniform(1, 3)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
        _cache["dark"] = img
    return _cache["dark"]

# ---------------------------------------------------------------- props
def trip_props(frame, d, T, sc):
    lt = T - sc["s"]
    # Sun far left, Uranus far right, a light ray crawling between
    d.ellipse([-120, 900, 120, 1140], fill=(255, 210, 80), outline=OUTL, width=6)
    uranus(frame, 900, 1020, 110, T, tilt=0, face=False)
    g = clamp((lt - 1.0) / 5.0)
    x1 = 130 + (770 - 130) * g
    d.line([(130, 1020), (x1, 1020)], fill=(255, 240, 150), width=10)
    d.ellipse([x1 - 14, 1006, x1 + 14, 1034], fill=(255, 250, 200))
    if lt > 0.5:
        top_label(frame, "2.9 BILLION KM", 380, YEL, 84)

def tilt_props(frame, d, T, sc):
    lt = T - sc["s"]
    t = 98.0 * ease_out(clamp((lt - 1.0) / 2.0))
    uranus(frame, 540, 1120, 210, T, tilt=t, face=True)
    if lt > 0.5:
        top_label(frame, f"TILT: {int(t)} DEGREES", 380, YEL, 76)

def fall_pos(T):
    return (540 + 60 * math.sin(T * 1.7), 1060 + 30 * math.sin(T * 2.3), 380)

def fall_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "NO GROUND", 380, YEL, 90)

def therm_props(frame, d, T, sc):
    lt = T - sc["s"]
    x = 860
    d.rounded_rectangle([x - 40, 760, x + 40, 1300], radius=40, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 75, 1260, x + 75, 1410], fill=(80, 150, 255), outline=OUTL, width=8)
    lvl = 1260 - 420 * (1 - ease_out(clamp((lt - 0.8) / 2.0)))
    d.rectangle([x - 20, lvl, x + 20, 1290], fill=(80, 150, 255))
    for k in range(8):
        y = 800 + k * 56
        d.line([(x + 40, y), (x + 70, y)], fill=WHITE, width=5)
    # frost dots
    rng = np.random.default_rng(7)
    for k in range(40):
        fx, fy = rng.uniform(0, W), rng.uniform(500, 1400)
        r = 3 + 2 * math.sin(T * 3 + k)
        d.ellipse([fx - r, fy - r, fx + r, fy + r], fill=(230, 245, 255))
    if lt > 0.5:
        n = -int(224 * clamp((lt - 0.5) / 2.3))
        top_label(frame, f"{n} °C", 380, YEL, 96)

def wind_pos(T):
    return (430 + 20 * math.sin(T * 9), 1100, 420)

def wind_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(10):
        y = 640 + k * 75
        x0 = (k * 173 + T * 1600) % 1500 - 300
        d.line([(x0, y), (x0 + 240, y)], fill=(230, 245, 255), width=6)
    # a plane racing alongside
    px = 1200 - ((lt * 380) % 1500)
    d.polygon([(px, 760), (px + 160, 740), (px + 190, 760), (px + 160, 780)], fill=WHITE, outline=OUTL)
    d.polygon([(px + 60, 760), (px + 120, 700), (px + 140, 760)], fill=(200, 210, 230), outline=OUTL)
    if lt > 0.5:
        top_label(frame, "900 KM/H", 380, YEL, 96)

def seasons_bg(T):
    if T - 39.0 < 3.4:
        if "daysky" not in _cache:
            _cache["daysky"] = E.grad([(0, (120, 200, 250)), (1, (220, 240, 255))], W, H).convert("RGBA")
        return _cache["daysky"]
    return dark_bg(T)

def seasons_props(frame, d, T, sc):
    lt = T - sc["s"]
    day = lt < 3.4
    if day:
        d.ellipse([700, 600, 900, 800], fill=(255, 220, 90), outline=OUTL, width=6)
        top_label(frame, "42 YEARS OF DAY", 380, YEL, 80)
    else:
        d.ellipse([700, 600, 900, 800], fill=(30, 40, 70), outline=(80, 90, 120), width=6)
        top_label(frame, "42 YEARS OF NIGHT", 380, (150, 190, 255), 80)
    d.rectangle([0, 1320, W, 1400], fill=(120, 200, 215) if day else (40, 70, 90), outline=OUTL, width=6)

def seasons_overlay(frame, T, sc):
    lt = T - sc["s"]
    if lt < 3.4:
        ov = Image.new("RGBA", (W, H), (255, 220, 140, 70))
        frame = frame.copy(); frame.alpha_composite(ov)
    return frame

def cake_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 790, 1220
    d.rounded_rectangle([cx - 160, cy - 60, cx + 160, cy + 120], radius=20, fill=(250, 190, 210), outline=OUTL, width=7)
    d.rounded_rectangle([cx - 160, cy - 60, cx + 160, cy], radius=20, fill=(255, 245, 250), outline=OUTL, width=7)
    d.rectangle([cx - 14, cy - 170, cx + 14, cy - 60], fill=(120, 190, 255), outline=OUTL, width=5)
    fl = 10 * math.sin(T * 12)
    d.polygon([(cx, cy - 235 + fl * 0.3), (cx + 18, cy - 185), (cx, cy - 170), (cx - 18, cy - 185)],
              fill=(255, 190, 50), outline=OUTL)
    l = label("1", 80, WHITE); comp(frame, l, cx - l.width / 2, cy + 10)
    if lt > 0.5:
        top_label(frame, "1 YEAR = 84 YEARS", 380, YEL, 76)

def egg_props(frame, d, T, sc):
    lt = T - sc["s"]
    # cracked egg on the left with green stink lines
    ex, ey = 260, 1160
    d.ellipse([ex - 110, ey - 140, ex + 110, ey + 140], fill=(250, 245, 230), outline=OUTL, width=8)
    d.line([(ex - 100, ey - 20), (ex - 50, ey - 50), (ex - 10, ey - 10), (ex + 40, ey - 60), (ex + 100, ey - 20)],
           fill=OUTL, width=7)
    for k in range(3):
        x = ex - 80 + k * 80
        pts = [(x + 18 * math.sin(T * 5 + j + k), ey - 170 - j * 32) for j in range(7)]
        d.line(pts, fill=(130, 200, 60), width=10, joint="curve")
    if lt > 0.5:
        top_label(frame, "ROTTEN EGGS?!", 380, YEL, 90)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="trip", s=4.0, e=11.0, bg="space", clock="DEPARTURE", props=trip_props,
         char="rocket", pos=(480, 1240, 260), look=(0.6, 0),
         narr="Uranus is 2.9 BILLION km from the Sun. Sunlight needs 2 H 40 MIN to arrive.",
         n_at=4.2, narr_y=1560),
    dict(id="tilt", s=11.0, e=18.0, bg="space", clock="FIRST LOOK", props=tilt_props,
         narr="Tipped over by 98 DEGREES, it rolls around the Sun on its SIDE.", n_at=11.2, narr_y=1560,
         say="Who knocked me OVER?", say_at=14.4, pitch=300),
    dict(id="fall", s=18.0, e=25.0, bg_fn=clouds_bg, clock="LANDING?", char="kid", pos=fall_pos,
         rot=lambda T: 20 * math.sin(T * 1.3), props=fall_props, look=(0, 0.5),
         narr="No ground to stand on. Just clouds, then a hot, dense, ICY fluid.", n_at=18.2,
         narr_y=1560, say="Where's the FLOOR?!", say_at=21.2, pitch=440),
    dict(id="cold", s=25.0, e=32.0, bg_fn=clouds_bg, clock="WEATHER CHECK", char="kid", state="puff",
         pos=(400, 1100, 400), props=therm_props, look=(0.6, -0.3),
         narr="Its air can drop to -224 °C, colder than Neptune in places.", n_at=25.2, narr_y=1560,
         say="My CHAI froze mid-SIP!", say_at=28.4, pitch=440),
    dict(id="wind", s=32.0, e=39.0, bg_fn=clouds_bg, clock="WIND ALERT", char="uncle", state="hat", pos=wind_pos,
         props=wind_props, look=(0.6, 0),
         narr="Winds race at up to 900 KM/H, about as fast as a cruising JET.", n_at=32.2, narr_y=1560,
         say="My HAT is in another CITY!", say_at=35.2, pitch=150),
    dict(id="seasons", s=39.0, e=46.0, bg_fn=seasons_bg, clock="SEASONS", char="kid", pos=(330, 1140, 380),
         props=seasons_props, look=(0.6, -0.5),
         narr="Near the poles, the Sun stays up 42 YEARS. Then: 42 years of NIGHT.", n_at=39.2,
         narr_y=1560, say="Good NIGHT... for 42 years?", say_at=42.6, pitch=440),
    dict(id="bday", s=46.0, e=TW, bg="living", clock="BIRTHDAY PLANS", char="kid", pos=(330, 1140, 380),
         props=cake_props, look=(0.6, -0.1),
         narr="One year here lasts 84 Earth years. Your 1st BIRTHDAY? Maybe never.", n_at=46.2, narr_y=1560,
         say="I'll be 84 at my FIRST party!", say_at=49.2, pitch=440),
    dict(id="twist", s=TW, e=60.0, bg="space", clock="PLOT TWIST", char="uncle", pos=(760, 1120, 400),
         props=egg_props, twist=True, look=(-0.6, 0.1),
         narr="Twist: its clouds hold hydrogen sulfide. Uranus would smell like ROTTEN EGGS.", n_at=TW + 0.2,
         narr_y=1560, say="Don't look at ME!", say_at=TW + 3.4, pitch=150),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        uranus(frame, 540, 1390 + 12 * math.sin(T * 2), 170 * p, T, tilt=98, face=True)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED ON", WHITE)], 120), 770, 0.75, "right"),
        (title([("URANUS?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" visit", WHITE)], 100), 470, 0.15),
                      (title([("Uranus?", YEL)], 96), 600, 0.45)],
               row=[("rocket", 1), ("earth", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, drums=False, melody=True),
           dict(t0=18.0, t1=39.0), dict(t0=39.0, t1=46.0, drums=False, minor=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=4.0, dur=14.0, g=0.25)],
    fx=[("whoosh", 5.0, 0.3), ("rumble", 12.0, 0.25, dict(dd=2.5)), ("wind", 18.2, 0.3, dict(dd=6.5)),
        ("wind", 25.2, 0.25, dict(dd=6.5)), ("gale", 32.2, 0.35, dict(dd=6.6)), ("ding", 42.4, 0.3),
        ("powerdown", 42.3, 0.3), ("pop", 47.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_on_uranus")
