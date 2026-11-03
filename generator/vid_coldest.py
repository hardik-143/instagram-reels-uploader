#!/usr/bin/env python3
"""What if you lived in the coldest village on Earth? Facts: Oymyakon, Sakha Republic (Yakutia), Siberia, ~500 people
(462 in 2010 census, ~560 est. 2021); January normal daily mean -45.7 C; official station record -67.7 C on 6 Feb 1933
(Wikipedia/Oymyakon; Scientific American 'Welcome to the Coldest Town on Earth'). Record high 34.6 C on 28 July 2010
(Wikipedia climate table) -> a swing of over 100 C. Permafrost, so no farming; diet of reindeer, horse meat, fish,
stroganina (frozen raw fish shaved thin) (Grunge; Yahoo/Telegraph). Eyelashes freeze, glasses stick to faces, pen ink
freezes, cars kept running all day or in heated garages (Yahoo/Telegraph; Grunge). School closes only below about
-52 to -55 C (SciAm -52, Wikipedia -55) -> 'about -50 C'. Home freezer ~ -18 C (standard). India: Dras, Ladakh,
~3,300 m, reportedly ~-60 C in winter 1995, often called the world's 2nd coldest inhabited place (The Better India;
Culture Trip)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
ICE = (120, 190, 255)

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

def snow(d, T, n=45, seed=5, speed=120):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        x = (x0 + 25 * math.sin(T * 1.3 + k)) % W
        y = (y0 + T * speed * (0.6 + (k % 5) * 0.15)) % H
        r = 4 + (k % 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

def thermo(frame, d, x, lt, target, t0=0.8, dur=2.2, top=870, col=ICE, rise=False):
    d.rounded_rectangle([x - 40, top, x + 40, 1300], radius=40, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 75, 1260, x + 75, 1410], fill=col, outline=OUTL, width=8)
    g = ease_out(clamp((lt - t0) / dur))
    f = g if rise else (1 - g)
    lvl = 1260 - (1260 - top - 40) * f * 0.85
    d.rectangle([x - 20, lvl, x + 20, 1290], fill=col)
    for k in range(8):
        y = top + 40 + k * 56
        d.line([(x + 40, y), (x + 70, y)], fill=OUTL, width=5)
    return g

_cache = {}
def snow_bg(T):
    if "snow" not in _cache:
        img = E.grad([(0, (150, 200, 250)), (0.65, (226, 240, 255)), (1, (226, 240, 255))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img); rng = np.random.default_rng(4)
        d.ellipse([-300, 1230, 700, 1460], fill=(240, 248, 255)); d.ellipse([300, 1210, 1400, 1460], fill=(232, 242, 255))
        d.rectangle([0, 1330, W, H], fill=(244, 250, 255))
        for _ in range(26):
            x, y = rng.uniform(0, W), rng.uniform(1380, H)
            d.ellipse([x - 34, y - 6, x + 34, y + 6], fill=(214, 228, 248))
        _cache["snow"] = img
    return _cache["snow"]

# ---------------------------------------------------------------- props
def village_props(frame, d, T, sc):
    lt = T - sc["s"]
    # little wooden houses with smoking chimneys
    for i, x in enumerate((120, 330, 760, 960)):
        y = 1330
        d.rectangle([x - 80, y - 120, x + 80, y], fill=(150, 95, 60), outline=OUTL, width=6)
        d.polygon([(x - 100, y - 115), (x, y - 200), (x + 100, y - 115)], fill=(245, 250, 255), outline=OUTL)
        d.rectangle([x - 25, y - 80, x + 25, y - 30], fill=(255, 220, 120), outline=OUTL, width=4)
        d.rectangle([x + 30, y - 190, x + 60, y - 140], fill=(110, 70, 50), outline=OUTL, width=4)
        for j in range(3):
            ph = (lt * 0.6 + j / 3 + i * 0.13) % 1.0
            r = 14 + 22 * ph
            cy = y - 210 - 160 * ph
            d.ellipse([x + 45 - r, cy - r, x + 45 + r, cy + r], fill=(225, 230, 240))
    snow(d, T)
    if lt > 0.5:
        top_label(frame, "OYMYAKON, SIBERIA", 380, YEL, 76)

def freezer_props(frame, d, T, sc):
    lt = T - sc["s"]
    # freezer on the right, thermometer on the left
    fx = 800
    d.rounded_rectangle([fx - 150, 820, fx + 150, 1330], radius=24, fill=(235, 240, 248), outline=OUTL, width=8)
    d.line([(fx - 150, 980), (fx + 150, 980)], fill=OUTL, width=6)
    d.rectangle([fx + 100, 870, fx + 116, 950], fill=(170, 180, 195), outline=OUTL, width=3)
    l = label("-18 °C", 60, (60, 120, 220)); comp(frame, l, fx - l.width / 2, 1080)
    thermo(frame, d, 230, lt, -46)
    snow(d, T, 30, 9)
    if lt > 0.5:
        n = -int(46 * clamp((lt - 0.5) / 2.2))
        top_label(frame, f"JANUARY: {n} °C", 380, YEL, 84)

def record_props(frame, d, T, sc):
    lt = T - sc["s"]
    thermo(frame, d, 860, lt, -68, col=(90, 150, 255))
    # frost crystals in corners
    for k in range(18):
        a = k * 0.35
        for cx, cy in ((0, 560), (W, 560)):
            x2 = cx + (1 if cx == 0 else -1) * (60 + 40 * (k % 4)) * math.cos(a % 1.5)
            y2 = cy + 200 * math.sin(a)
            d.line([(cx, cy), (x2, y2)], fill=(225, 240, 255), width=4)
    snow(d, T, 40, 11, 180)
    if lt > 0.5:
        n = -67.7 * clamp((lt - 0.5) / 2.2)
        top_label(frame, f"RECORD: {n:.1f} °C", 380, YEL, 84)

def car_pos(T):
    return (430, 1170, 420)

def car_props(frame, d, T, sc):
    lt = T - sc["s"]
    # exhaust puffs behind the auto (to its right)
    for j in range(6):
        ph = (lt * 0.9 + j / 6) % 1.0
        r = 20 + 60 * ph
        x = 690 + 300 * ph
        y = 1260 - 60 * ph
        col = int(200 + 40 * ph)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(col, col, min(255, col + 10)))
    snow(d, T, 30, 13)
    if lt > 0.5:
        top_label(frame, "ENGINE ON. ALL DAY.", 380, YEL, 76)

def fish_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a plate of shaved frozen fish curls on the right
    px, py = 780, 1260
    d.ellipse([px - 200, py - 50, px + 200, py + 50], fill=WHITE, outline=OUTL, width=7)
    for k in range(7):
        x = px - 150 + k * 50
        d.arc([x - 30, py - 70, x + 30, py - 10], 180, 360, fill=(250, 225, 230), width=14)
    mini(frame, "fish", px, py - 230 + 10 * math.sin(T * 3), 230, T, look=(-0.6, 0.1),
         talk=max(0, math.sin(T * 9)) * (1 if 3.0 < lt < 5.5 else 0))
    if lt > 0.5:
        top_label(frame, "FROZEN RAW FISH", 380, YEL, 84)

def school_props(frame, d, T, sc):
    lt = T - sc["s"]
    # school sign + bag
    d.rectangle([700, 760, 1000, 900], fill=(250, 245, 220), outline=OUTL, width=7)
    l = label("SCHOOL", 56, OUTL if False else (60, 60, 80)); comp(frame, l, 850 - l.width / 2, 795)
    d.rectangle([840, 900, 860, 1330], fill=(120, 80, 50), outline=OUTL, width=4)
    bx, by = 560, 1250
    d.rounded_rectangle([bx - 70, by - 90, bx + 70, by + 80], radius=24, fill=(240, 80, 80), outline=OUTL, width=7)
    d.arc([bx - 40, by - 140, bx + 40, by - 60], 180, 360, fill=OUTL, width=8)
    snow(d, T, 40, 17, 160)
    if lt > 0.5:
        top_label(frame, "OPEN TILL ~ -50 °C", 380, YEL, 80)

def mountains(d, col=(200, 215, 235)):
    d.polygon([(-50, 1340), (250, 820), (520, 1340)], fill=col, outline=OUTL)
    d.polygon([(250, 820), (200, 905), (300, 905)], fill=WHITE)
    d.polygon([(380, 1340), (720, 760), (1130, 1340)], fill=(185, 200, 225), outline=OUTL)
    d.polygon([(720, 760), (660, 860), (785, 860)], fill=WHITE)

def dras_props(frame, d, T, sc):
    lt = T - sc["s"]
    mountains(d)
    d.rectangle([0, 1330, W, 1400], fill=(244, 250, 255))
    # sign post
    d.rectangle([820, 1060, 840, 1340], fill=(120, 80, 50), outline=OUTL, width=4)
    d.rectangle([680, 975, 990, 1075], fill=(250, 210, 80), outline=OUTL, width=6)
    l = label("DRAS", 60, (60, 40, 30)); comp(frame, l, 835 - l.width / 2, 992)
    snow(d, T, 35, 21)
    if lt > 0.5:
        top_label(frame, "LADAKH, INDIA", 380, YEL, 84)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    thermo(frame, d, 880, lt, 35, t0=0.6, dur=1.8, col=(255, 90, 60), rise=True)
    mini(frame, "sun", 210, 1010 + 10 * math.sin(T * 2), 240, T, look=(0.4, 0.3))
    # heat waves
    for k in range(4):
        x = 140 + k * 120
        pts = [(x + 14 * math.sin(T * 6 + j + k), 1320 - j * 30) for j in range(7)]
        d.line(pts, fill=(255, 150, 80), width=6, joint="curve")
    if lt > 0.5:
        top_label(frame, "SUMMER: +34.6 °C", 380, YEL, 84)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="village", s=4.0, e=11.0, bg_fn=snow_bg, clock="WELCOME", props=village_props, char="kid", state="puff",
         pos=(540, 1180, 340), look=(0, 0.3),
         narr="Oymyakon in Siberia: about 500 people live in the COLDEST town on Earth.", n_at=4.2, narr_y=1560),
    dict(id="freezer", s=11.0, e=18.0, bg_fn=snow_bg, clock="JANUARY", props=freezer_props, char="uncle", state="hat",
         pos=(500, 1130, 360), look=(0.6, 0),
         narr="January averages about -46 °C. Your deep FREEZER is only -18 °C.", n_at=11.2, narr_y=1560,
         say="My freezer is WARMER?!", say_at=14.2, pitch=150),
    dict(id="record", s=18.0, e=25.0, bg_fn=snow_bg, clock="RECORD DAY", props=record_props, char="kid", state="puff",
         pos=(420, 1120, 400), look=(0.5, -0.3),
         narr="Official record: -67.7 °C. Eyelashes freeze, glasses STICK, pen ink stops.", n_at=18.2,
         narr_y=1560, say="My EYELASHES are crunchy!", say_at=21.2, pitch=440),
    dict(id="car", s=25.0, e=32.0, bg_fn=snow_bg, clock="TRAFFIC", props=car_props, char="auto", pos=car_pos,
         look=(-0.4, 0),
         narr="Cars stay RUNNING all day or sleep in heated garages. Switch off = frozen.", n_at=25.2,
         narr_y=1560, say="Never switch me OFF!", say_at=28.4, pitch=260),
    dict(id="food", s=32.0, e=39.0, bg_fn=snow_bg, clock="DINNER", props=fish_props, char="uncle", state="hat",
         pos=(300, 1130, 380), look=(0.6, 0),
         narr="The ground stays FROZEN, so no farms. Dinner: raw frozen fish, shaved thin.", n_at=32.2,
         narr_y=1560, say="Fish KULFI, anyone?", say_at=35.2, pitch=150),
    dict(id="school", s=39.0, e=46.0, bg_fn=snow_bg, clock="MONDAY 8 AM", props=school_props, char="kid",
         state="puff", pos=(300, 1140, 360), look=(0.6, -0.3),
         narr="School only shuts below about -50 °C. At -40? Pack your BAG.", n_at=39.2, narr_y=1560,
         say="No SNOW DAY for me?!", say_at=42.2, pitch=440),
    dict(id="dras", s=46.0, e=TW, bg_fn=snow_bg, clock="MEANWHILE IN INDIA", props=dras_props, char="uncle",
         state="hat", pos=(330, 1160, 360), look=(0.6, -0.2),
         narr="India's own freezer: DRAS in Ladakh reportedly hit about -60 °C in 1995.", n_at=46.2,
         narr_y=1560, say="Chai, but make it HOT!", say_at=49.2, pitch=150),
    dict(id="twist", s=TW, e=60.0, bg="hot", clock="PLOT TWIST", char="uncle", pos=(560, 1150, 360),
         props=twist_props, twist=True, look=(0.6, -0.2),
         narr="Twist: Oymyakon once hit +34.6 °C in summer. A swing of over 100 DEGREES!", n_at=TW + 0.2,
         narr_y=1560, say="Where's my SWEATER... and my FAN?", say_at=TW + 3.2, pitch=150),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        s = int(300 * p)
        if s > 4:
            spr = draw_char("kid", s, T, 0, False, (0, 0.2), "puff")
            comp(frame, spr, 540 - s / 2, 1390 - s / 2 + 10 * math.sin(T * 2))
    snow(d, T, 35, 3)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED IN THE", WHITE)], 110), 770, 0.75, "right"),
        (title([("COLDEST VILLAGE?", YEL)], 120), 905, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Could ", WHITE), ("YOU", YEL), (" survive", WHITE)], 100), 470, 0.15),
                      (title([("-67 °C?", YEL)], 96), 600, 0.45)],
               row=[("kid", "puff"), ("uncle", "hat"), ("auto", 1), ("fish", 1), ("sun", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=39.0), dict(t0=39.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, melody=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=18.0, dur=7.0, g=0.2)],
    fx=[("wind", 4.2, 0.3, dict(dd=6.5)), ("wind", 11.2, 0.25, dict(dd=6.5)), ("gale", 18.2, 0.3, dict(dd=6.6)),
        ("rumble", 25.4, 0.25, dict(dd=6.0)), ("pop", 33.0, 0.3), ("wind", 39.2, 0.2, dict(dd=6.5)),
        ("whistle", 40.0, 0.2), ("wind", 46.2, 0.25, dict(dd=6.5))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_in_the_coldest_village")
