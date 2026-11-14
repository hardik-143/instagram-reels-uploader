#!/usr/bin/env python3
"""What if humans could photosynthesise? Facts: chlorophyll absorbs mostly red and blue light and reflects green.
Photosynthesis: sunlight + water + CO2 -> sugar + oxygen. Most of India receives 4-7 kWh of solar energy per sq m
per day, with 250-300 clear sunny days a year (Invest India / MNRE). Adult skin area ~1.8-2 sq m; only about half
faces the Sun at once (we use 1 sq m). Max solar-to-biomass efficiency is 4.6% for C3 plants, 6% for C4 (Zhu, Long &
Ort 2008, Curr Opin Biotech). Best case: 1 sq m x 5 kWh x 4.6% = 0.23 kWh = ~200 kcal a day, less than one samosa
(~250 kcal). An adult needs ~2,000 kcal a day (ICMR-NIN 2020: ~1,660-2,110 kcal sedentary) -> ~10 sq m of sunlit
green skin, about a 10x10 ft room (9.3 sq m). Twist: the sea slug Elysia chlorotica (US East Coast, 2.5-5 cm)
keeps chloroplasts from the algae it eats, turning emerald green, and can go nine months or more without eating
(National Geographic)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite
from vid_salt_slug import slug

TW = 56.0
GREEN = (110, 200, 90)

# ------------------------------------------------ a green-skinned kid ("greenkid")
_orig_draw_char = E.draw_char
SKIN = np.array((242, 194, 152), np.int16)
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind != "greenkid":
        return _orig_draw_char(kind, B, T, talk, blink, look, state)
    spr = _orig_draw_char("kid", B, T, talk, blink, look, state)
    a = np.array(spr).astype(np.int16)
    dist = np.abs(a[..., :3] - SKIN).sum(-1)
    m = (dist < 40) & (a[..., 3] > 0)
    a[m, 0], a[m, 1], a[m, 2] = GREEN
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
E.draw_char = draw_char

_txt = {}
def label(txt, size=56, col=WHITE, stroke=8):
    k = (txt, size, col, stroke)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=stroke)
    return _txt[k]

def center_label(frame, txt, x, y, col=YEL, size=64, stroke=8):
    l = label(txt, size, col, stroke)
    comp(frame, l, x - l.width / 2, y - l.height / 2)

_gl = {}
def glow(frame, x, y, r, col=(255, 230, 120), s=0.7):
    k = (int(r), col, round(s, 2))
    if k not in _gl:
        R = max(2, int(r))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        q = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / R, 0, 1) ** 2
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (q * 255 * s).astype(np.uint8)
        _gl[k] = Image.fromarray(arr, "RGBA")
    g = _gl[k]
    frame.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

def sunrays(frame, d, T, x, y, n=10, r0=90, r1=150):
    glow(frame, x, y, 240)
    for k in range(n):
        a = k * 2 * math.pi / n + T * 0.4
        d.line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))],
               fill=(255, 210, 60), width=10)
    d.ellipse([x - 80, y - 80, x + 80, y + 80], fill=(255, 210, 60), outline=OUTL, width=5)

def leaf(d, x, y, s, ang=0.0, col=(80, 170, 70)):
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((t, 0.35 * math.sin(math.pi * t)))
    for i in range(21):
        t = 1 - i / 20
        pts.append((t, -0.35 * math.sin(math.pi * t)))
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts]
    d.polygon(P, fill=col, outline=OUTL, width=4)
    d.line([P[0], (x + s * ca, y + s * sa)], fill=(40, 110, 40), width=3)

# ---------------------------------------------------------------- scene props
def rgb_props(frame, d, T, sc):
    lt = T - sc["s"]
    sunrays(frame, d, T, 880, 470)
    for k, col in enumerate(((240, 70, 70), (70, 200, 90), (70, 120, 240))):
        p = clamp((lt - 0.6 - k * 0.3) / 1.0)
        if p <= 0: continue
        y0 = 560 + k * 40
        x1 = 800 - 380 * p
        d.line([(800, y0), (x1, y0 + 260 * p)], fill=col, width=12)
    if lt > 2.2:
        center_label(frame, "RED + BLUE: EATEN", 800, 860, (255, 140, 140), 46)

def recipe(frame, d, T, sc):
    lt = T - sc["s"]
    items = [("SUN", (255, 210, 60)), ("WATER", (90, 170, 250)), ("CO2", (200, 200, 210))]
    for k, (t, col) in enumerate(items):
        p = ease_back(clamp((lt - 0.3 - k * 0.4) / 0.4))
        if p <= 0: continue
        x = 220 + k * 320; y = 820
        d.ellipse([x - 110 * p, y - 110 * p, x + 110 * p, y + 110 * p], fill=col, outline=OUTL, width=5)
        center_label(frame, t, x, y, WHITE, 46)
        if k < 2 and p > 0.9: center_label(frame, "+", x + 160, y, WHITE, 70)
    if lt > 2.0:
        center_label(frame, "=", 540, 980, YEL, 90)
    if lt > 2.5:
        for k, (t, col) in enumerate((("SUGAR", (255, 255, 255)), ("OXYGEN", (140, 220, 250)))):
            x = 330 + k * 420; y = 1140
            d.rounded_rectangle([x - 150, y - 60, x + 150, y + 60], 26, fill=(70, 160, 80), outline=OUTL, width=5)
            center_label(frame, t, x, y, col, 50)

def india_sun(frame, d, T, sc):
    lt = T - sc["s"]
    sunrays(frame, d, T, 820, 480)
    if lt > 1.6:
        center_label(frame, "4-7 kWh / SQ M / DAY", 540, 760, YEL, 60)

def skin_props(frame, d, T, sc):
    lt = T - sc["s"]
    sunrays(frame, d, T, 900, 450, r0=70, r1=110)
    p = ease_out(clamp((lt - 1.0) / 1.0))
    if p > 0:
        d.rounded_rectangle([70, 700, 70 + 520 * p, 810], 24, fill=(255, 255, 255), outline=OUTL, width=5)
        if p > 0.9: center_label(frame, "2 SQ M SKIN", 330, 755, YEL, 52)
    q = ease_out(clamp((lt - 2.6) / 1.0))
    if q > 0:
        d.rounded_rectangle([70, 860, 70 + 260 * q, 970], 24, fill=(255, 210, 60), outline=OUTL, width=5)
        if q > 0.9: center_label(frame, "SUNLIT", 200, 915, WHITE, 48)

def eff_props(frame, d, T, sc):
    lt = T - sc["s"]
    x0, x1, y = 120, 960, 1000
    d.rounded_rectangle([x0, y - 50, x1, y + 50], 25, fill=(255, 230, 120), outline=OUTL, width=5)
    p = ease_out(clamp((lt - 1.2) / 1.0))
    w = (x1 - x0) * 0.046 * p
    if w > 4:
        d.rounded_rectangle([x0, y - 50, x0 + max(w, 50), y + 50], 25, fill=(70, 170, 70), outline=OUTL, width=5)
    center_label(frame, "SUNLIGHT", 540, y - 110, WHITE, 52)
    if lt > 2.2:
        center_label(frame, "4.6% = FOOD", 330, y + 130, YEL, 66)
        center_label(frame, "THE REST: LOST", 680, y + 230, WHITE, 52)

def kcal_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.2:
        center_label(frame, "~200 KCAL", 540, 900, YEL, 80)

def room_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 1.0) / 1.4))
    s = 120 + 420 * p
    d.rectangle([540 - s / 2, 1000 - s / 2, 540 + s / 2, 1000 + s / 2], fill=(110, 200, 90), outline=OUTL, width=6)
    for k in range(1, 5):
        xx = 540 - s / 2 + k * s / 5
        d.line([(xx, 1000 - s / 2), (xx, 1000 + s / 2)], fill=(80, 160, 70), width=3)
    if p > 0.95:
        center_label(frame, "~10 SQ M", 540, 1000, WHITE, 64)

def tree_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([230, 640, 290, 1330], fill=(120, 80, 50), outline=OUTL, width=5)
    rng = np.random.default_rng(3)
    for k in range(26):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(40, 230)
        x = 230 + 0.8 * r * math.cos(a); y = 480 + 0.55 * r * math.sin(a)
        leaf(d, x, y, 90 + 10 * math.sin(lt * 2 + k), a + 0.2 * math.sin(lt * 1.5 + k))

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    sunrays(frame, d, T, 880, 440, r0=60, r1=100)
    slug(frame, 520, 1200, 760, T, col=(70, 190, 90), wig=0.6)
    if lt > 3.5:
        center_label(frame, "9+ MONTHS", 520, 760, YEL, 80)
        center_label(frame, "WITHOUT EATING!", 520, 850, WHITE, 60)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="green", s=4.0, e=10.5, bg="day", clock="DAY 1", char="greenkid", pos=(420, 1080, 420),
         props=rgb_props, look=(0.5, -0.4),
         narr="CHLOROPHYLL in your skin eats red and blue light and bounces back GREEN.", n_at=4.2,
         say="I'm GREEN now!", say_at=7.4, pitch=640),
    dict(id="recipe", s=10.5, e=17.0, bg="day", clock="RECIPE", props=recipe,
         narr="SUNLIGHT + WATER + CO2 makes SUGAR, plus OXYGEN to breathe out.", n_at=10.7),
    dict(id="india", s=17.0, e=23.5, bg="hot", clock="NOON", char="greenkid", pos=(400, 1080, 400),
         props=india_sun, look=(0.6, -0.5),
         narr="Most of India gets 4 to 7 kWh of sunshine per square metre a DAY.", n_at=17.2),
    dict(id="skin", s=23.5, e=30.0, bg="day", clock="2 SQ M", char="greenkid", pos=(770, 1100, 360),
         props=skin_props, look=(0.4, -0.4),
         narr="Your skin is about 2 SQ M, but only about HALF faces the Sun.", n_at=23.7),
    dict(id="eff", s=30.0, e=36.5, bg="day", clock="4.6%", props=eff_props,
         narr="And even the BEST plants turn only ~4.6% of sunlight into food.", n_at=30.2),
    dict(id="kcal", s=36.5, e=43.0, bg="hot", clock="FULL DAY", char="samosa", pos=(540, 1160, 320),
         props=kcal_props, look=(0, 0),
         narr="A whole sunny day: about 200 KCAL. Less than ONE SAMOSA!", n_at=36.7,
         say="That's ALL?", say_at=39.8, pitch=500),
    dict(id="need", s=43.0, e=49.5, bg="day", clock="2,000 KCAL", props=room_props,
         narr="You need ~2,000 KCAL a day: sunlit skin as big as a 10x10 FT ROOM.", n_at=43.2),
    dict(id="trees", s=49.5, e=TW, bg="day", clock="TREES", char="flower", pos=(720, 1080, 360),
         props=tree_props, look=(-0.4, -0.2),
         narr="That's why trees spread out HUGE leaves and stand still all day.", n_at=49.7,
         say="Welcome to MY life!", say_at=52.5, pitch=560),
    dict(id="twist", s=TW, e=64.0, bg="day", clock="WAIT...", props=twist_props, twist=True,
         narr="Twist: this SEA SLUG steals chloroplasts from the algae it EATS!", n_at=56.9),
    dict(id="outro", s=64.0, e=69.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("greenkid", 300, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=69.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("HUMANS COULD", WHITE)], 130), 770, 0.75, "right"),
        (title([("PHOTOSYNTHESISE?", YEL)], 110), 920, 1.2, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" trade lunch", WHITE)], 84), 450, 0.15),
                      (title([("for sunshine?", WHITE)], 90), 570, 0.45)],
               row=[("greenkid", 1), ("sun", 1), ("flower", 1), ("samosa", 1), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=64.0, t1=69.0, melody=True)],
    fx=[("pop", 11.0, 0.3), ("pop", 11.4, 0.3), ("pop", 11.8, 0.3), ("ding", 13.2, 0.3),
        ("click", 31.4, 0.4), ("wind", 49.6, 0.3, dict(dd=6.0)),
        ("bubbles", TW + 1.0, 0.15, dict(dd=6.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_photosynth")
