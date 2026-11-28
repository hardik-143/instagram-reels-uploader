#!/usr/bin/env python3
"""What if you counted every star in the sky? Facts: in a large city you may see only the brightest dozen stars; on a
clear moonless night far from city lights about 2,000 (Caltech IPAC Cool Cosmos; EarthSky ~2,000-2,500 at once).
Whole-sky naked-eye total, both hemispheres: about 9,000-10,000 (EarthSky: 9,096; 'close to 10,000' upper end).
Hanle, Ladakh: declared India's first dark sky reserve in December 2022, ~22 km radius around Hanle, home of the Indian
Astronomical Observatory of IIA Bengaluru (IIAP HDSR page). Milky Way: 100 to 400 billion stars (Space.com citing ESA's
Jos de Bruijne; ESA ~100 thousand million). 100 billion seconds = ~3,170 years. Universe: roughly 10^22 to 10^24 stars
(ESA); Universe Today estimates ~5 sextillion beach sand grains and likely 5-10x more stars than sand grains. Geminids
peak 13-14 Dec 2026 under a ~18% crescent Moon (EarthSky). Twist: the Sun is a star you can count in daylight."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0

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

_rng = np.random.default_rng(11)
STARS = [(_rng.uniform(20, W - 20), _rng.uniform(330, 1250), _rng.uniform(1.2, 4.2), _rng.uniform(0, 6.3))
         for _ in range(900)]

def starfield(d, T, n, ymax=1250, twinkle=True):
    for i in range(min(n, len(STARS))):
        x, y, r, ph = STARS[i]
        if y > ymax: continue
        rr = r * (0.75 + 0.25 * math.sin(T * 3 + ph)) if twinkle else r
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 250, 230))

def bright(d, x, y, r, T, ph=0):
    rr = r * (0.85 + 0.15 * math.sin(T * 3 + ph))
    d.line([(x - rr * 2.4, y), (x + rr * 2.4, y)], fill=(255, 250, 220), width=3)
    d.line([(x, y - rr * 2.4), (x, y + rr * 2.4)], fill=(255, 250, 220), width=3)
    d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 252, 235))

# ---------------------------------------------------------------- backgrounds
_cache = {}
def city_bg(T):
    if "city" not in _cache:
        img = E.grad([(0, (40, 34, 70)), (0.55, (110, 70, 90)), (0.7, (200, 120, 90)), (1, (60, 50, 70))],
                     W, H).convert("RGBA")
        d = ImageDraw.Draw(img); rng = np.random.default_rng(4)
        x = 0
        while x < W:
            bw = rng.integers(90, 170); top = rng.integers(950, 1180)
            d.rectangle([x, top, x + bw, 1340], fill=(46, 40, 66), outline=OUTL, width=4)
            for yy in range(int(top) + 25, 1320, 55):
                for xx in range(int(x) + 18, int(x + bw) - 24, 38):
                    if rng.uniform() < 0.6:
                        d.rectangle([xx, yy, xx + 18, yy + 26], fill=(255, 214, 120))
            x += bw + rng.integers(4, 14)
        d.rectangle([0, 1340, W, H], fill=(52, 46, 62))
        _cache["city"] = img
    img = _cache["city"].copy(); d = ImageDraw.Draw(img)
    pts = [(160, 420), (380, 560), (620, 470), (860, 600), (250, 760), (720, 820), (960, 420), (470, 680),
           (110, 900), (900, 860), (560, 360), (330, 920)]
    for k, (x, y) in enumerate(pts):
        bright(d, x, y, 5, T, k)
    return img

def dark_bg(T, n=900):
    key = "dark"
    if key not in _cache:
        img = E.grad([(0, (4, 6, 22)), (0.6, (14, 20, 50)), (1, (20, 26, 60))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.polygon([(0, 1340), (0, 1180), (180, 1060), (330, 1150), (520, 1000), (700, 1130), (880, 1040),
                   (1080, 1170), (1080, 1340)], fill=(30, 34, 56), outline=OUTL)
        d.rectangle([0, 1340, W, H], fill=(36, 40, 60))
        d.line([(0, 1340), (W, 1340)], fill=OUTL, width=6)
        _cache[key] = img
    img = _cache[key].copy(); d = ImageDraw.Draw(img)
    starfield(d, T, n, ymax=1100)
    return img

def dark_full(T): return dark_bg(T)

def galaxy_bg(T):
    if "gal" not in _cache:
        img = E.grad([(0, (6, 4, 24)), (1, (24, 10, 48))], W, H).convert("RGBA")
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        rng = np.random.default_rng(8)
        for k in range(5000):
            arm = k % 2
            t = rng.uniform(0.1, 1.0)
            a = arm * math.pi + t * 4.2 + rng.normal(0, 0.22)
            rr = 40 + t * 430
            x = 540 + rr * math.cos(a); y = 880 + rr * math.sin(a) * 0.55
            c = 255 - int(60 * t)
            rr = rng.uniform(1.0, 2.6)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(c, c - 20, 255 - int(80 * (1 - t)), 255))
        img.alpha_composite(lay)
        dc = ImageDraw.Draw(img)
        for k in range(18):
            r = 170 - k * 9; f = k / 17
            col = (int(40 + 215 * f), int(24 + 210 * f), int(70 + 120 * f))
            dc.ellipse([540 - r, 880 - r * 0.55, 540 + r, 880 + r * 0.55], fill=col)
        _cache["gal"] = img
    return _cache["gal"]

def beach_bg(T):
    if "beach" not in _cache:
        img = E.grad([(0, (6, 8, 30)), (0.55, (20, 30, 70)), (0.56, (30, 80, 130)), (0.68, (30, 80, 130)),
                      (0.69, (226, 196, 140)), (1, (210, 178, 120))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img); rng = np.random.default_rng(2)
        for _ in range(2500):
            x, y = rng.uniform(0, W), rng.uniform(1330, H)
            d.point((x, y), fill=(170, 140, 90))
        for _ in range(600):
            x, y = rng.uniform(0, W), rng.uniform(300, 1050)
            r = rng.uniform(0.8, 2.6)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 230))
        _cache["beach"] = img
    return _cache["beach"]

# ---------------------------------------------------------------- props
def city_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = min(12, int(12 * clamp((lt - 0.4) / 2.5)) + (1 if lt > 0.4 else 0))
    if lt > 0.4:
        top_label(frame, f"STARS: {min(n, 12)}", 380, YEL, 100)

def dark_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.4) / 3.0))
    if lt > 0.4:
        top_label(frame, f"STARS: {int(2000 * g):,}", 380, YEL, 100)

def dark_scene_bg(T):
    lt = T - 11.0
    n = int(60 + 840 * ease_out(clamp((lt - 0.4) / 3.0)))
    return dark_bg(T, n)

def hanle_props(frame, d, T, sc):
    lt = T - sc["s"]
    # observatory dome on a ridge
    x, base = 780, 1060
    d.rectangle([x - 90, base - 70, x + 90, base + 30], fill=(230, 232, 240), outline=OUTL, width=6)
    d.pieslice([x - 100, base - 170, x + 100, base + 30], 180, 360, fill=(240, 242, 248), outline=OUTL, width=6)
    sw = 20 + 6 * math.sin(T)
    d.polygon([(x - sw, base - 165), (x + sw, base - 165), (x + sw, base - 75), (x - sw, base - 75)],
              fill=(30, 30, 50))
    if lt > 0.5:
        top_label(frame, "HANLE, LADAKH", 380, YEL, 96)
    if lt > 2.2:
        at_label(frame, "DARK SKY RESERVE", 540, 570, WHITE, 56)

def hemi_props(frame, d, T, sc):
    lt = T - sc["s"]
    # two hemisphere domes
    for cx, lab in ((300, "NORTH"), (780, "SOUTH")):
        d.chord([cx - 210, 860, cx + 210, 1280], 180, 360, fill=(20, 26, 60), outline=OUTL, width=6)
        rng = np.random.default_rng(cx)
        k = int(40 * clamp((lt - 0.5) / 2.0))
        for _ in range(k):
            a = rng.uniform(math.pi, 2 * math.pi); r = rng.uniform(0, 190)
            px, py = cx + r * math.cos(a), 1070 + r * math.sin(a)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 250, 230))
        d.line([(cx - 210, 1070), (cx + 210, 1070)], fill=OUTL, width=6)
        at_label(frame, lab, cx, 1120, WHITE, 48)
    if lt > 0.5:
        g = ease_out(clamp((lt - 0.5) / 3.0))
        top_label(frame, f"TOTAL: {int(9000 * g):,}", 380, YEL, 96)
    if lt > 3.8:
        at_label(frame, "(MAX ~10,000)", 540, 570, WHITE, 52)

def mw_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "100-400 BILLION", 380, YEL, 96)

def count_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = clamp((lt - 0.8) / 4.2) ** 2
    yrs = int(3170 * g)
    if lt > 0.5:
        top_label(frame, "1 STAR A SECOND", 380, YEL, 84)
    if lt > 0.8:
        at_label(frame, f"{yrs:,} YEARS", 540, 1260, YEL, 96)

def count_clock(T):
    lt = T - 39.0
    g = clamp((lt - 0.8) / 4.2) ** 2
    return f"COUNTED: {int(100 * g)} BILLION"

def sand_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "STARS > SAND GRAINS", 380, YEL, 80)

def day_bg_fn(T):
    if "day" not in _cache:
        img = E.grad([(0, (90, 170, 250)), (0.7, (196, 232, 255)), (1, (196, 232, 255))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1340, W, H], fill=(120, 190, 110))
        d.line([(0, 1340), (W, 1340)], fill=OUTL, width=6)
        _cache["day"] = img
    return _cache["day"]

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "STARS: 1", 380, YEL, 110)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="city", s=4.0, e=11.0, bg_fn=city_bg, clock="BIG CITY NIGHT", char="kid",
         pos=(540, 1250, 300), props=city_props, look=(0, -0.7),
         narr="From a big city, you may see only the brightest DOZEN stars.", n_at=4.2, narr_y=1560,
         say="That's IT?!", say_at=7.6, pitch=440),
    dict(id="dark", s=11.0, e=18.0, bg_fn=dark_scene_bg, clock="NO CITY LIGHTS", char="kid",
         pos=(540, 1250, 300), props=dark_props, look=(0.3, -0.7),
         narr="Go somewhere truly DARK and about 2,000 stars appear at once.", n_at=11.2, narr_y=1560,
         say="Where were you ALL hiding?", say_at=14.4, pitch=440),
    dict(id="hanle", s=18.0, e=25.0, bg_fn=dark_full, clock="MEANWHILE IN INDIA", char="uncle", state="hat",
         pos=(300, 1240, 300), props=hanle_props, look=(0.6, -0.4),
         narr="India's first DARK SKY reserve: Hanle, LADAKH, declared in 2022.", n_at=18.2, narr_y=1560,
         say="Lights OFF, stars ON!", say_at=21.4, pitch=150),
    dict(id="hemi", s=25.0, e=32.0, bg="space", clock="WHOLE PLANET", props=hemi_props,
         char="earth", pos=(540, 1290, 170), state=0,
         narr="Count BOTH halves of the sky and your eyes top out near 9,000-10,000.", n_at=25.2,
         narr_y=1580, say="That's my LIMIT?", say_at=28.4, pitch=300),
    dict(id="mw", s=32.0, e=39.0, bg_fn=galaxy_bg, clock="OUR GALAXY", props=mw_props,
         char="kid", pos=(170, 1320, 230), look=(0.7, -0.5),
         narr="But our Milky Way holds 100 to 400 BILLION stars.", n_at=32.2, narr_y=1580,
         say="BILLION?!", say_at=35.4, pitch=440),
    dict(id="count", s=39.0, e=46.0, bg_fn=dark_full, clock=count_clock, props=count_props,
         char="kid", state="puff", pos=(540, 1000, 300), look=(0, -0.5),
         narr="Counting 100 billion, one per second, nonstop? Over 3,000 YEARS.", n_at=39.2, narr_y=1560,
         say="Ek, do, teen... HELP!", say_at=42.4, pitch=440),
    dict(id="sand", s=46.0, e=TW, bg_fn=beach_bg, clock="WHOLE UNIVERSE", props=sand_props,
         char="uncle", state="hat", pos=(300, 1270, 300), look=(0.5, -0.6),
         narr="The Universe likely has more stars than all the SAND on Earth's beaches.",
         n_at=46.2, narr_y=1560, say="Every BEACH?!", say_at=49.6, pitch=150),
    dict(id="twist", s=TW, e=61.0, bg_fn=day_bg_fn, clock="PLOT TWIST", props=twist_props, twist=True,
         char="sun", pos=(540, 1050, 380),
         narr="Twist: you can count one star in broad DAYLIGHT. The SUN.",
         n_at=TW + 0.2, narr_y=1560, say="Counted me YET?", say_at=TW + 3.4, pitch=300),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.15)
        for k, (x, y) in enumerate(((300, 1480), (540, 1420), (780, 1500), (420, 1620), (680, 1640))):
            bright(d, x, y, 10 * p, T, k)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU COUNTED", WHITE)], 120), 770, 0.75, "right"),
        (title([("EVERY STAR?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("How many stars can ", WHITE)], 84), 470, 0.15),
                      (title([("YOU", YEL), (" see tonight?", WHITE)], 96), 600, 0.45)],
               row=[("moon", 1), ("kid", 1), ("sun", 1), ("earth", 0), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, drums=False, melody=True),
           dict(t0=18.0, t1=32.0, melody=True), dict(t0=32.0, t1=46.0, drums=False, minor=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=66.0, melody=True)],
    drones=[dict(t0=32.0, dur=14.0, g=0.22)],
    fx=[("crowd", 4.3, 0.12, dict(dd=6.0)), ("ding", 12.0, 0.2), ("click", 19.0, 0.3), ("ding", 26.0, 0.2),
        ("rumble", 32.5, 0.2, dict(dd=4.0)), ("tick", 40.0, 0.2), ("tick", 41.0, 0.2), ("tick", 42.0, 0.2),
        ("waves", 46.3, 0.3, dict(dd=6.0)), ("pop", 54.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_counted_every_star")
