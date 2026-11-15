#!/usr/bin/env python3
"""What if you lived on Venus? Facts: nearly Earth-sized and comes closer to Earth than any other planet; surface ~460-465 C,
hot enough to melt lead (lead melts at 327 C); surface pressure ~92 bar, like ~1 km underwater (Planetary Society,
'What would it be like to stand on the surface of Venus', 2023); clouds of sulfuric acid; Venera 13 survived 127 minutes on
the surface in March 1982 (Guinness World Records); Venus spins backwards, so the Sun rises in the west; one spin takes
~243 Earth days, one orbit ~225 (Caltech IPAC Cool Cosmos); India's cabinet approved ISRO's Venus Orbiter Mission
(Shukrayaan) on 18 Sep 2024, launch planned March 2028 (Space.com). Twist: a little above 50 km the pressure is ~1 bar,
temperatures 0-50 C, gravity ~90% of Earth's, and breathable air (O2/N2) is a lifting gas there (Landis, NASA NTRS
20030022668; NASA HAVOC concept via IEEE Spectrum)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
CREAM = (240, 205, 130)
SWIRL = (215, 165, 85)

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

def venus(frame, cx, cy, r, T, face=True):
    """Creamy-yellow cloud-covered planet with soft swirl bands."""
    S = int(r * 2.4)
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = S / 2
    d.ellipse([c - r - 6, c - r - 6, c + r + 6, c + r + 6], fill=OUTL)
    d.ellipse([c - r, c - r, c + r, c + r], fill=CREAM)
    for k, off in ((-0.55, 0.0), (-0.15, 1.3), (0.3, 2.1), (0.65, 0.7)):
        y = c + k * r
        w = math.sqrt(max(0, 1 - k * k)) * r * 0.9
        pts = [(c - w + j * (2 * w / 12), y + r * 0.05 * math.sin(j * 0.9 + T * 1.5 + off)) for j in range(13)]
        d.line(pts, fill=SWIRL, width=max(2, int(r * 0.08)), joint="curve")
    if face:
        ex = r * 0.32; ey = c - r * 0.1; er = r * 0.13
        for sx in (-1, 1):
            d.ellipse([c + sx * ex - er, ey - er * 1.1, c + sx * ex + er, ey + er * 1.1], fill=WHITE, outline=OUTL,
                      width=max(2, int(r * 0.03)))
            d.ellipse([c + sx * ex - er * 0.5, ey - er * 0.4, c + sx * ex + er * 0.3, ey + er * 0.6], fill=(25, 20, 30))
        d.arc([c - r * 0.25, c + r * 0.1, c + r * 0.25, c + r * 0.4], 20, 160, fill=OUTL, width=max(2, int(r * 0.05)))
    comp(frame, L, cx - S / 2, cy - S / 2)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def surface_bg(T):
    if "surf" not in _cache:
        img = E.grad([(0, (200, 120, 40)), (0.55, (240, 170, 70)), (1, (150, 80, 30))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1330, W, H], fill=(120, 65, 30))
        rng = np.random.default_rng(5)
        for k in range(14):
            x = rng.uniform(0, W); y = rng.uniform(1360, 1900); r = rng.uniform(20, 60)
            d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=(95, 50, 25))
        d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
        _cache["surf"] = img
    img = _cache["surf"].copy(); d = ImageDraw.Draw(img)
    for k in range(6):  # heat shimmer
        y = 1290 - k * 18
        pts = [(x, y + 6 * math.sin(x / 40 + T * 6 + k)) for x in range(0, W + 40, 40)]
        d.line(pts, fill=(255, 210, 120), width=3)
    return img

def cloud_bg(T):
    if "cloud" not in _cache:
        _cache["cloud"] = E.grad([(0, (240, 200, 120)), (0.6, (250, 225, 160)), (1, (225, 175, 90))], W, H).convert("RGBA")
    img = _cache["cloud"].copy(); d = ImageDraw.Draw(img)
    for k in range(8):
        y = 560 + k * 170
        x = (k * 311 + T * 90) % 1500 - 250
        for dx, r in ((-90, 70), (0, 100), (90, 70)):
            d.ellipse([x + dx - r, y - r * 0.5, x + dx + r, y + r * 0.5], fill=(252, 238, 195))
    return img

# ---------------------------------------------------------------- props
def twin_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = min(ease_back(clamp((lt - 0.3) / 0.5)), 1.1)
    venus(frame, 300, 1060, 200 * p, T, face=True)
    if lt > 0.8:
        spr = draw_char("earth", int(420 * min(ease_back(clamp((lt - 0.8) / 0.5)), 1.1)) + 2, T, 0.0, False, (-0.6, 0), T)
        comp(frame, spr, 780 - spr.width / 2, 1060 - spr.height / 2)
    if lt > 0.5:
        top_label(frame, "EARTH'S TWIN?", 380, YEL, 90)
    if lt > 1.2:
        at_label(frame, "VENUS", 300, 1320, CREAM, 60)
        at_label(frame, "EARTH", 780, 1320, (150, 210, 255), 60)

def therm(frame, d, T, lt, x=840, frac=1.0, col=(240, 70, 50)):
    d.rounded_rectangle([x - 40, 760, x + 40, 1240], radius=40, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 75, 1200, x + 75, 1350], fill=col, outline=OUTL, width=8)
    lvl = 1230 - 420 * frac
    d.rectangle([x - 20, lvl, x + 20, 1230], fill=col)
    for k in range(8):
        y = 800 + k * 52
        d.line([(x + 40, y), (x + 70, y)], fill=WHITE, width=5)

def heat_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.6) / 2.4))
    therm(frame, d, T, lt, frac=g)
    if lt > 0.5:
        top_label(frame, f"{int(465 * g)} °C", 380, YEL, 110)
    if lt > 3.2:
        # a lead block melting into a puddle
        m = clamp((lt - 3.2) / 2.0)
        bx, by = 220, 1330
        h = 110 * (1 - m)
        d.rectangle([bx - 70, by - h, bx + 70, by], fill=(140, 150, 165), outline=OUTL, width=6)
        d.ellipse([bx - 70 - 60 * m, by - 14, bx + 70 + 60 * m, by + 22], fill=(160, 170, 185), outline=OUTL, width=5)
        at_label(frame, "LEAD", bx, by - 150, WHITE, 50)

def press_pos(T):
    return (430, 1130, 400)

def press_props(frame, d, T, sc):
    lt = T - sc["s"]
    # pressure gauge on the right
    cx, cy, r = 830, 1000, 150
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=OUTL, width=10)
    for k in range(9):
        a = math.radians(225 - k * 33.75)
        d.line([(cx + math.cos(a) * r * 0.75, cy - math.sin(a) * r * 0.75),
                (cx + math.cos(a) * r * 0.9, cy - math.sin(a) * r * 0.9)], fill=OUTL, width=6)
    g = ease_out(clamp((lt - 0.6) / 2.0))
    a = math.radians(225 - 270 * g + 3 * math.sin(T * 20) * g)
    d.line([(cx, cy), (cx + math.cos(a) * r * 0.7, cy - math.sin(a) * r * 0.7)], fill=(230, 50, 40), width=10)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=OUTL)
    at_label(frame, f"{max(1, int(92 * g))}x", cx, cy + r + 50, YEL, 70)
    # pressure arrows replaced by squeezing bars (no arrow glyphs)
    s = 30 * math.sin(T * 6)
    d.rectangle([150 - s, 760, 190 - s, 1340], fill=(170, 110, 50), outline=OUTL, width=5)
    d.rectangle([670 + s, 760, 710 + s, 1340], fill=(170, 110, 50), outline=OUTL, width=5)
    if lt > 0.5:
        top_label(frame, "LIKE 1 KM UNDER THE SEA", 380, YEL, 68)

def acid_props(frame, d, T, sc):
    lt = T - sc["s"]
    # green-yellow acid drops falling
    for k in range(18):
        x = (k * 137) % 1040 + 20
        y = (k * 211 + T * 520) % 900 + 520
        d.ellipse([x - 9, y - 14, x + 9, y + 14], fill=(190, 230, 60), outline=OUTL, width=3)
    # lander probe on the ground
    px, py = 720, 1180
    d.ellipse([px - 120, py - 40, px + 120, py + 40], fill=(180, 185, 195), outline=OUTL, width=7)
    d.rectangle([px - 70, py - 150, px + 70, py - 30], fill=(205, 210, 220), outline=OUTL, width=7)
    d.ellipse([px - 40, py - 230, px + 40, py - 150], fill=(160, 170, 185), outline=OUTL, width=7)
    mins = min(127, int(127 * clamp((lt - 0.8) / 4.2)))
    if lt < 5.0:
        at_label(frame, f"{mins} MIN", px, py - 290, YEL, 70)
    else:
        at_label(frame, "SIGNAL LOST", px, py - 290, (255, 120, 110), 60)
    if lt > 0.5:
        top_label(frame, "SULFURIC ACID CLOUDS", 380, YEL, 72)

def sun_rise_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.5) / 3.0))
    sx, sy = 230, 1320 - 420 * g
    d.ellipse([sx - 110, sy - 110, sx + 110, sy + 110], fill=(255, 225, 120), outline=OUTL, width=7)
    d.rectangle([0, 1330, W, H], fill=(120, 65, 30))
    d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
    at_label(frame, "WEST", 230, 1375, YEL, 60)
    at_label(frame, "EAST", 850, 1375, WHITE, 60)
    if lt > 0.5:
        top_label(frame, "SPINS BACKWARDS", 380, YEL, 86)

def day_props(frame, d, T, sc):
    lt = T - sc["s"]
    g1 = ease_out(clamp((lt - 0.5) / 1.8))
    g2 = ease_out(clamp((lt - 2.0) / 1.8))
    x0 = 140
    d.rounded_rectangle([x0, 940, x0 + 780 * g1 + 10, 1010], radius=20, fill=(255, 160, 60), outline=OUTL, width=6)
    d.rounded_rectangle([x0, 1130, x0 + 722 * g2 + 10, 1200], radius=20, fill=(120, 200, 255), outline=OUTL, width=6)
    if lt > 0.6: comp(frame, label("1 SPIN: 243 DAYS", 54, WHITE), x0, 860)
    if lt > 2.1: comp(frame, label("1 YEAR: 225 DAYS", 54, WHITE), x0, 1050)
    if lt > 0.5:
        top_label(frame, "DAY > YEAR", 380, YEL, 96)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    venus(frame, 820, 760, 120, T, face=True)
    if lt > 0.5:
        top_label(frame, "SHUKRAYAAN: 2028", 380, YEL, 82)

def rocket_pos(T):
    lt = T - 46.0
    return (360 + 60 * clamp((lt - 3.5) / 3.0), 1250 - 140 * ease_out(clamp((lt - 3.5) / 3.0)), 330)

def balloon_pos(T):
    return (540, 1100 + 25 * math.sin(T * 1.6), 280)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    by = 1100 + 25 * math.sin(T * 1.6)
    # big transparent air bubble/balloon habitat around the kid
    d.ellipse([540 - 240, by - 290, 540 + 240, by + 150], outline=(255, 255, 255), width=10)
    d.ellipse([540 - 170, by - 240, 540 - 110, by - 180], fill=(255, 255, 255))
    d.line([(540 - 200, by + 100), (540 - 60, by + 230)], fill=OUTL, width=5)
    d.line([(540 + 200, by + 100), (540 + 60, by + 230)], fill=OUTL, width=5)
    d.rectangle([540 - 70, by + 225, 540 + 70, by + 260], fill=(160, 110, 70), outline=OUTL, width=5)
    if lt > 0.5:
        top_label(frame, "50 KM UP: 1 ATMOSPHERE", 380, YEL, 70)
    if lt > 2.6:
        top_label(frame, "0 TO 50 °C", 495, WHITE, 64)

def twist_after(frame, d, T, sc):
    pass

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="twin", s=4.0, e=11.0, bg="space", clock="MEET VENUS", props=twin_props,
         narr="Venus is nearly Earth's size, and comes CLOSER to us than any planet.",
         n_at=4.2, narr_y=1560),
    dict(id="heat", s=11.0, e=18.0, bg_fn=surface_bg, clock="LANDING", char="kid", state="puff",
         pos=(470, 1120, 380), props=heat_props, look=(0.6, -0.3),
         narr="The ground is about 465 °C. Hot enough to MELT LEAD.", n_at=11.2, narr_y=1560,
         say="My CHAPPAL just melted!", say_at=14.2, pitch=440),
    dict(id="press", s=18.0, e=25.0, bg_fn=surface_bg, clock="PRESSURE CHECK", char="kid", pos=press_pos,
         props=press_props, look=(0.5, 0),
         narr="The air presses about 92 TIMES harder, like 1 KM under the sea.", n_at=18.2, narr_y=1560,
         say="I'm a SQUASHED samosa!", say_at=21.2, pitch=440),
    dict(id="acid", s=25.0, e=32.0, bg_fn=surface_bg, clock="WEATHER CHECK", char="uncle", state="hat",
         pos=(300, 1120, 380), props=acid_props, look=(0.6, 0),
         narr="ACID clouds. The toughest lander, VENERA 13, lasted 127 MINUTES.", n_at=25.2,
         narr_y=1560, say="Even ROBOTS quit here!", say_at=28.6, pitch=150),
    dict(id="sunrise", s=32.0, e=39.0, bg_fn=surface_bg, clock="MORNING", char="kid", pos=(620, 1150, 360),
         props=sun_rise_props, look=(-0.6, -0.4),
         narr="Venus spins BACKWARDS, so the Sun rises in the WEST.", n_at=32.2, narr_y=1560,
         say="Sun, WRONG side!", say_at=35.2, pitch=440),
    dict(id="day", s=39.0, e=46.0, bg="space", clock="CALENDAR", char="kid", pos=(880, 1330, 220),
         props=day_props, look=(0, -0.5),
         narr="One spin takes 243 EARTH DAYS. One trip round the Sun: just 225.", n_at=39.2,
         narr_y=1560, say="My DAY beats my YEAR?", say_at=42.4, pitch=440),
    dict(id="india", s=46.0, e=TW, bg="space", clock="INDIA CALLING", char="rocket", pos=rocket_pos,
         props=india_props, look=(0.6, -0.4),
         narr="India's SHUKRAYAAN orbiter is planned to launch in 2028.", n_at=46.2, narr_y=1560,
         say="Next stop: SHUKRA!", say_at=49.0, pitch=300),
    dict(id="twist", s=TW, e=61.0, bg_fn=cloud_bg, clock="PLOT TWIST", char="kid", pos=balloon_pos,
         props=twist_props, twist=True, look=(0, -0.3),
         narr="Twist: up there, plain AIR is lighter than Venus air. Your home would FLOAT.",
         n_at=TW + 0.2, narr_y=1560, say="Best VIEW in town!", say_at=TW + 3.6, pitch=440),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        venus(frame, 540, 1390 + 12 * math.sin(T * 2), 170 * p, T, face=True)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED ON", WHITE)], 120), 770, 0.75, "right"),
        (title([("VENUS?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" live", WHITE)], 100), 470, 0.15),
                      (title([("in the clouds?", YEL)], 96), 600, 0.45)],
               row=[("rocket", 1), ("earth", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, drums=False, melody=True),
           dict(t0=11.0, t1=32.0, minor=True), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=66.0, melody=True)],
    drones=[dict(t0=11.0, dur=21.0, g=0.22)],
    fx=[("whoosh", 5.0, 0.3), ("rumble", 11.2, 0.25, dict(dd=3.0)), ("crash", 18.6, 0.2),
        ("rumble", 19.0, 0.25, dict(dd=4.0)), ("bubbles", 25.4, 0.25), ("powerdown", 30.2, 0.3),
        ("ding", 33.5, 0.25), ("tick", 40.5, 0.3), ("tick", 42.0, 0.3), ("rumble", 49.5, 0.35, dict(dd=3.0)),
        ("wind", TW + 0.5, 0.25, dict(dd=7.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_on_venus")
