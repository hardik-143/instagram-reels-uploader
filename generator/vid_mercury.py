#!/usr/bin/env python3
"""What if you lived on Mercury? Facts: ESA-JAXA BepiColombo entered Mercury orbit on 21 Nov 2026, about 8 years after
its Oct 2018 launch (ESA 'Latest updates: BepiColombo's arrival at Mercury', 23 Nov 2026; Space.com 3 Sep 2026);
from Mercury the Sun looks more than 3x as large and up to 7x brighter; days up to 430 C, nights down to -180 C;
one solar day (sunrise to sunrise) = 176 Earth days, one year = 88 Earth days; from some places the Sun rises
briefly, sets and rises again; possible water ice in permanently shadowed polar craters (NASA science.nasa.gov/mercury/facts;
ESA 'Meet Mercury'). Twist: on average Mercury is the closest planet to Earth (1.04 AU vs Venus 1.14 AU) and to every
other planet (Stockman, Monroe & Cordner, Physics Today, 12 Mar 2019)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 60.0
GREY = (168, 160, 152)
DARK = (120, 112, 106)

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

def mercury(frame, cx, cy, r, T, face=True):
    """Small grey cratered planet."""
    if r < 4: return
    S = int(r * 2.4)
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = S / 2
    d.ellipse([c - r - 6, c - r - 6, c + r + 6, c + r + 6], fill=OUTL)
    d.ellipse([c - r, c - r, c + r, c + r], fill=GREY)
    for (dx, dy, k) in ((-0.5, -0.5, 0.16), (0.45, -0.45, 0.12), (-0.55, 0.45, 0.13), (0.5, 0.5, 0.18),
                        (0.0, -0.75, 0.09), (0.75, 0.05, 0.08), (-0.8, 0.0, 0.08)):
        rr = r * k
        x, y = c + dx * r, c + dy * r
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=DARK, outline=(100, 94, 88), width=max(1, int(r * 0.02)))
    if face:
        ex = r * 0.32; ey = c - r * 0.05; er = r * 0.14
        for sx in (-1, 1):
            d.ellipse([c + sx * ex - er, ey - er * 1.1, c + sx * ex + er, ey + er * 1.1], fill=WHITE, outline=OUTL,
                      width=max(2, int(r * 0.03)))
            d.ellipse([c + sx * ex - er * 0.5, ey - er * 0.4, c + sx * ex + er * 0.3, ey + er * 0.6], fill=(25, 20, 30))
        d.arc([c - r * 0.25, c + r * 0.15, c + r * 0.25, c + r * 0.45], 20, 160, fill=OUTL, width=max(2, int(r * 0.05)))
    comp(frame, L, cx - S / 2, cy - S / 2)

def sun_disc(d, cx, cy, r, col=(255, 220, 110)):
    for k in range(12):
        a = k * math.pi / 6
        d.line([(cx + math.cos(a) * r * 1.1, cy + math.sin(a) * r * 1.1),
                (cx + math.cos(a) * r * 1.35, cy + math.sin(a) * r * 1.35)], fill=col, width=10)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=OUTL, width=7)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def ground(img, col=(130, 122, 114)):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1330, W, H], fill=col)
    rng = np.random.default_rng(7)
    for k in range(16):
        x = rng.uniform(0, W); y = rng.uniform(1370, 1900); r = rng.uniform(20, 70)
        d.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4], fill=(105, 98, 92), outline=(90, 84, 78), width=3)
    d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
    return img

def day_bg(T):
    if "day" not in _cache:
        img = E.grad([(0, (10, 8, 24)), (0.7, (30, 24, 50)), (1, (40, 32, 60))], W, H).convert("RGBA")
        _cache["day"] = ground(img, (175, 160, 140))
    img = _cache["day"].copy(); d = ImageDraw.Draw(img)
    for k in range(6):  # heat shimmer
        y = 1290 - k * 18
        pts = [(x, y + 6 * math.sin(x / 40 + T * 6 + k)) for x in range(0, W + 40, 40)]
        d.line(pts, fill=(255, 200, 120), width=3)
    return img

def night_bg(T):
    if "night" not in _cache:
        img = E.grad([(0, (4, 4, 14)), (1, (12, 14, 34))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(3)
        for k in range(90):
            x = rng.uniform(0, W); y = rng.uniform(0, 1300); r = rng.uniform(1.5, 4)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 230, 255))
        _cache["night"] = ground(img, (80, 84, 100))
    return _cache["night"].copy()

# ---------------------------------------------------------------- props
def probe(d, cx, cy, s=1.0):
    d.rectangle([cx - 60 * s, cy - 50 * s, cx + 60 * s, cy + 50 * s], fill=(220, 200, 140), outline=OUTL, width=6)
    for sx in (-1, 1):
        x0 = cx + sx * 70 * s; x1 = cx + sx * 260 * s
        d.rectangle([min(x0, x1), cy - 30 * s, max(x0, x1), cy + 30 * s], fill=(60, 90, 170), outline=OUTL, width=5)
        for k in range(1, 4):
            x = x0 + (x1 - x0) * k / 4
            d.line([(x, cy - 30 * s), (x, cy + 30 * s)], fill=(140, 170, 230), width=3)
    d.ellipse([cx - 22 * s, cy - 92 * s, cx + 22 * s, cy - 50 * s], fill=WHITE, outline=OUTL, width=4)

def news_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = min(ease_back(clamp((lt - 0.2) / 0.6)), 1.1)
    mercury(frame, 540, 1080, 230 * p, T, face=True)
    a = T * 0.9
    px, py = 540 + math.cos(a) * 380, 1080 + math.sin(a) * 140
    probe(d, px, py, 0.55)
    if lt > 0.4:
        top_label(frame, "ARRIVED: 21 NOV 2026", 380, YEL, 80)

def sun_props(frame, d, T, sc):
    lt = T - sc["s"]
    g1 = ease_out(clamp((lt - 0.4) / 1.0)); g2 = ease_out(clamp((lt - 2.2) / 1.6))
    sun_disc(d, 230, 960, 60 * g1 + 1)
    sun_disc(d, 760, 960, 170 * g2 + 1, (255, 235, 150))
    if lt > 1.0: at_label(frame, "FROM EARTH", 230, 1120, WHITE, 44)
    if lt > 3.0: at_label(frame, "FROM MERCURY", 790, 1200, YEL, 44)
    if lt > 0.4: top_label(frame, "3x BIGGER SUN", 380, YEL, 90)

def therm(d, x, frac, col):
    d.rounded_rectangle([x - 40, 820, x + 40, 1180], radius=40, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 75, 1140, x + 75, 1290], fill=col, outline=OUTL, width=8)
    lvl = 1170 - 330 * frac
    d.rectangle([x - 20, lvl, x + 20, 1170], fill=col)

def hot_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.5) / 2.4))
    therm(d, 860, g, (240, 70, 50))
    if lt > 0.4: top_label(frame, f"{int(430 * g)} °C", 380, YEL, 110)

def cold_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.5) / 2.4))
    therm(d, 860, 1 - 0.92 * g, (90, 160, 240))
    # frost sparkles
    for k in range(10):
        x = (k * 173) % 1000 + 40; y = 1250 + (k * 37) % 70
        s = 10 + 6 * math.sin(T * 4 + k)
        d.line([(x - s, y), (x + s, y)], fill=WHITE, width=3); d.line([(x, y - s), (x, y + s)], fill=WHITE, width=3)
    if lt > 0.4: top_label(frame, f"{-int(180 * g)} °C", 380, (150, 210, 255), 110)

def cal_props(frame, d, T, sc):
    lt = T - sc["s"]
    g1 = ease_out(clamp((lt - 0.5) / 1.8)); g2 = ease_out(clamp((lt - 2.2) / 1.8))
    x0 = 130
    d.rounded_rectangle([x0, 960, x0 + 400 * g1 + 10, 1030], radius=20, fill=(120, 200, 255), outline=OUTL, width=6)
    d.rounded_rectangle([x0, 1150, x0 + 800 * g2 + 10, 1220], radius=20, fill=(255, 160, 60), outline=OUTL, width=6)
    if lt > 0.6: comp(frame, label("1 YEAR: 88 DAYS", 54, WHITE), x0, 880)
    if lt > 2.3: comp(frame, label("SUNRISE TO SUNRISE: 176", 54, WHITE), x0, 1070)
    if lt > 0.4: top_label(frame, "1 DAY = 2 YEARS", 380, YEL, 96)

def wobble_props(frame, d, T, sc):
    lt = T - sc["s"]
    # sun peeks up, dips back, rises again
    p = clamp((lt - 0.4) / 5.5)
    if p < 0.35: h = p / 0.35 * 120
    elif p < 0.55: h = 120 - (p - 0.35) / 0.2 * 90
    else: h = 30 + (p - 0.55) / 0.45 * 330
    sun_disc(d, 760, 1330 - h, 150, (255, 235, 150))
    img = frame  # redraw ground in front of the sun
    d.rectangle([0, 1330, W, 1530], fill=(175, 160, 140))
    d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
    if lt > 0.4: top_label(frame, "RISE, SET, RISE AGAIN", 380, YEL, 76)

def ice_props(frame, d, T, sc):
    lt = T - sc["s"]
    # crater in deep shadow with ice on its floor
    d.ellipse([480, 1180, 1040, 1330], fill=(40, 40, 60), outline=OUTL, width=7)
    d.ellipse([560, 1230, 960, 1310], fill=(200, 235, 255), outline=(120, 170, 220), width=4)
    for k in range(6):
        x = 600 + k * 60; s = 8 + 5 * math.sin(T * 5 + k)
        d.line([(x - s, 1262), (x + s, 1262)], fill=WHITE, width=3); d.line([(x, 1262 - s), (x, 1262 + s)], fill=WHITE, width=3)
    if lt > 1.6: at_label(frame, "NEVER SEES THE SUN", 760, 1130, WHITE, 44)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    spr = draw_char("earth", 300, T, 0.0, False, (0.6, 0), T)
    comp(frame, spr, 250 - spr.width / 2, 1000 - spr.height / 2)
    mercury(frame, 800, 1000, 110 * min(ease_back(clamp((lt - 0.4) / 0.5)), 1.1), T, face=True)
    if lt > 1.2:
        at_label(frame, "VENUS: 1.14 AU", 540, 760, WHITE, 52)
        at_label(frame, "MERCURY: 1.04 AU", 540, 840, YEL, 56)
    if lt > 0.4: top_label(frame, "AVERAGE DISTANCE", 380, YEL, 84)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="news", s=4.0, e=11.0, bg="space", clock="BIG SPACE NEWS", props=news_props,
         narr="Europe and Japan's BEPICOLOMBO just reached MERCURY, 8 YEARS after launch.",
         n_at=4.2, narr_y=1560),
    dict(id="sun", s=11.0, e=18.0, bg_fn=day_bg, clock="LOOK UP", char="kid", pos=(540, 1270, 200),
         props=sun_props, look=(0.5, -0.5),
         narr="The Sun looks over 3 TIMES bigger and up to 7 TIMES brighter.", n_at=11.2, narr_y=1560,
         say="I need BIGGER shades!", say_at=14.4, pitch=440),
    dict(id="hot", s=18.0, e=25.0, bg_fn=day_bg, clock="DAYTIME", char="kid", state="puff",
         pos=(430, 1120, 380), props=hot_props, look=(0.6, -0.3),
         narr="Daytime ground can hit about 430 °C. No air to cool you.", n_at=18.2, narr_y=1560,
         say="My chai is BOILING!", say_at=21.2, pitch=440),
    dict(id="cold", s=25.0, e=32.0, bg_fn=night_bg, clock="NIGHT TIME", char="uncle", state="hat",
         pos=(400, 1120, 380), props=cold_props, look=(0.6, 0),
         narr="Same planet at NIGHT: about MINUS 180 °C. Brrr.", n_at=25.2, narr_y=1560,
         say="Where's my SWEATER?!", say_at=28.2, pitch=150),
    dict(id="cal", s=32.0, e=39.0, bg="space", clock="CALENDAR", char="kid", pos=(880, 1360, 200),
         props=cal_props, look=(0, -0.5),
         narr="A year is 88 DAYS. Sunrise to sunrise takes 176 Earth days!", n_at=32.2, narr_y=1560,
         say="2 BIRTHDAYS before dinner!", say_at=35.2, pitch=440),
    dict(id="wobble", s=39.0, e=46.0, bg_fn=day_bg, clock="MORNING", char="kid", pos=(300, 1180, 320),
         props=wobble_props, look=(0.6, -0.3),
         narr="From some spots the Sun RISES, SETS again, then rises AGAIN.", n_at=39.2, narr_y=1560,
         say="Sun, make up your MIND!", say_at=42.4, pitch=440),
    dict(id="ice", s=46.0, e=53.0, bg_fn=night_bg, clock="NORTH POLE", char="kid", pos=(260, 1180, 320),
         props=ice_props, look=(0.6, 0.2),
         narr="Yet deep polar craters in PERMANENT shadow may hide WATER ICE.", n_at=46.2, narr_y=1560,
         say="ICE on the Sun's NEIGHBOUR?", say_at=49.2, pitch=440),
    dict(id="hint", s=53.0, e=TW, bg="space", clock="QUIZ TIME", char="earth", pos=(540, 1080, 380),
         narr="Quick quiz: which planet is CLOSEST to Earth? Most say VENUS...", n_at=53.2, narr_y=1560,
         say="VENUS, obviously!", say_at=56.0, pitch=300),
    dict(id="twist", s=TW, e=67.5, bg="space", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: ON AVERAGE, Mercury is closest to Earth, and to EVERY planet.",
         n_at=TW + 0.2, narr_y=1560),
    dict(id="outro", s=67.5, e=72.5),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        mercury(frame, 540, 1390 + 12 * math.sin(T * 2), 170 * p, T, face=True)

cfg = dict(
    total=72.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED ON", WHITE)], 120), 770, 0.75, "right"),
        (title([("MERCURY?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" live", WHITE)], 100), 470, 0.15),
                      (title([("on Mercury?", YEL)], 96), 600, 0.45)],
               row=[("rocket", 1), ("earth", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0, minor=True), dict(t0=32.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.5, t1=72.5, melody=True)],
    drones=[dict(t0=25.0, dur=7.0, g=0.18), dict(t0=46.0, dur=7.0, g=0.15)],
    fx=[("whoosh", 5.0, 0.3), ("ding", 12.8, 0.2), ("rumble", 18.4, 0.25, dict(dd=3.0)),
        ("wind", 25.3, 0.25, dict(dd=6.0)), ("tick", 33.5, 0.3), ("tick", 35.0, 0.3), ("ding", 41.5, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_on_mercury")
