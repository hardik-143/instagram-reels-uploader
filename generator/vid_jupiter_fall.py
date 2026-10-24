#!/usr/bin/env python3
"""What if you fell into Jupiter? Escape speed 59.5 km/s (~200,000 km/h on arrival, NASA fact sheet); no solid surface,
mostly hydrogen + helium; gravity ~2.5x Earth (NASA: 2.53 equatorial / 2.64 mean at 1 bar); Galileo probe (1995)
measured ~650 km/h winds, lasted 58 minutes, ~200 km deep, 24 atm / 152 C; Great Red Spot wider than Earth;
deep hydrogen turns liquid / metallic; core ~24,000 C (NASA Space Place) vs Sun surface ~5,500 C;
Jupiter = Guru / Brihaspati, Thursday = Guruvar.
Twist: NASA crashed the Galileo orbiter into Jupiter on purpose (21 Sep 2003) so it could never hit Europa
and contaminate it with Earth microbes."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def jupiter(d, cx, cy, r, T, face=True):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(222, 170, 120), outline=OUTL, width=6)
    bands = [(-0.62, (190, 130, 90)), (-0.3, (240, 214, 176)), (0.05, (196, 120, 80)), (0.38, (236, 200, 160)),
             (0.66, (184, 128, 92))]
    for f, col in bands:
        y = cy + f * r; h = 0.1 * r
        half = math.sqrt(max(0, 1 - ((abs(f) + 0.1) ** 2))) * r * 0.97
        d.rounded_rectangle([cx - half, y - h, cx + half, y + h], radius=h, fill=col)
    d.ellipse([cx + 0.15 * r, cy + 0.42 * r, cx + 0.5 * r, cy + 0.62 * r], fill=(200, 90, 70))
    if face:
        e = 0.11 * r
        for ex in (cx - 0.3 * r, cx + 0.05 * r):
            d.ellipse([ex - e, cy - 0.25 * r - e * 1.1, ex + e, cy - 0.25 * r + e * 1.1], fill=WHITE, outline=OUTL, width=4)
            d.ellipse([ex - e * 0.45, cy - 0.25 * r - e * 0.5, ex + e * 0.45, cy - 0.25 * r + e * 0.5], fill=(25, 20, 30))
        d.arc([cx - 0.28 * r, cy - 0.12 * r, cx + 0.05 * r, cy + 0.08 * r], 20, 160, fill=OUTL, width=6)

# ---------------------------------------------------------------- falling-through-clouds backgrounds
def band_tex(pal, seed):
    """Tall band texture (W x 3H) with wavy horizontal stripes."""
    rng = np.random.default_rng(seed)
    hh = 3 * H
    y = np.arange(hh)[:, None].astype(np.float32)
    x = np.arange(W)[None, :].astype(np.float32)
    ph = rng.uniform(0, 6.28, 4)
    v = (np.sin(y / 70 + 0.9 * np.sin(x / 210 + ph[0]) + ph[1]) * 0.5
         + np.sin(y / 23 + 0.6 * np.sin(x / 120 + ph[2])) * 0.3 + np.sin(y / 190 + ph[3]) * 0.2)
    v = (v - v.min()) / (v.max() - v.min())
    c0, c1, c2 = [np.array(c, np.float32) for c in pal]
    t = v[..., None]
    img = np.where(t < 0.5, c0 + (c1 - c0) * (t / 0.5), c1 + (c2 - c1) * ((t - 0.5) / 0.5))
    arr = np.zeros((hh, W, 4), np.uint8); arr[..., :3] = img.clip(0, 255); arr[..., 3] = 255
    return Image.fromarray(arr, "RGBA")

PALS = {
    "cloud": [(196, 132, 88), (238, 206, 162), (250, 236, 210)],
    "deep": [(120, 60, 40), (176, 96, 60), (214, 140, 90)],
    "metal": [(40, 20, 30), (110, 40, 40), (190, 80, 50)],
    "core": [(140, 30, 10), (230, 110, 30), (255, 220, 120)],
}
_tex = {}
def fall_bg(pal, speed=420, sideways=0.0):
    cache = {}
    def f(T):
        key = int(T * 30)
        if key in cache: return cache[key]
        if pal not in _tex: _tex[pal] = band_tex(PALS[pal], len(pal) * 7)
        tex = _tex[pal]
        oy = int((T * speed) % (2 * H))
        img = tex.crop((0, oy, W, oy + H))
        if sideways:
            ox = int((T * sideways) % W)
            img = Image.fromarray(np.roll(np.array(img), -ox, axis=1), "RGBA")
        cache.clear(); cache[key] = img
        return img
    return f

def fall_pos(base_y=1060, B=420, sway=40):
    return lambda T: (540 + sway * math.sin(T * 1.7), base_y + 20 * math.sin(T * 2.3), B)

def fall_rot(T): return 14 * math.sin(T * 1.3)

def streaks(d, T, col=(255, 255, 255)):
    for i in range(10):
        x = 80 + (i * 97) % 920
        y = (i * 311 - T * 1800) % (H + 300) - 150
        d.line([(x, y), (x, y + 140)], fill=col, width=5)

# ---------------------------------------------------------------- scenes
def approach_bg(T):
    img = E.bg("space").copy()
    d = ImageDraw.Draw(img)
    lt = max(0.0, T - 4.0)
    r = 260 + 520 * ease_out(clamp(lt / 7.0))
    jupiter(d, 540, 1780 + r * 0.25, r, T, face=False)
    return img

def approach_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "~200,000 KM/H", 380, YEL, 76)

def ground_props(frame, d, T, sc):
    streaks(d, T)
    lt = T - sc["s"]
    if lt > 3.4: top_label(frame, "NO SOLID SURFACE", 380, YEL, 66)

def gravity_props(frame, d, T, sc):
    streaks(d, T)
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "~2.5x EARTH GRAVITY", 380, YEL, 62)

def wind_props(frame, d, T, sc):
    for i in range(9):
        y = 420 + i * 120
        x = (i * 263 + T * 1600) % (W + 400) - 300
        d.line([(x, y), (x + 220, y)], fill=WHITE, width=6)
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "~650 KM/H WINDS", 380, YEL, 70)

def spot_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp((lt - 0.3) / 0.6))
    if p > 0.02:
        cx, cy = 540, 650
        rx, ry = 330 * p, 170 * p
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(206, 96, 70), outline=OUTL, width=6)
        d.ellipse([cx - rx * 0.7, cy - ry * 0.6, cx + rx * 0.7, cy + ry * 0.6], fill=(226, 130, 96))
        d.ellipse([cx - rx * 0.35, cy - ry * 0.3, cx + rx * 0.35, cy + ry * 0.3], fill=(240, 164, 120))
    if lt > 1.2: top_label(frame, "GREAT RED SPOT", 380, YEL, 70)

def probe(d, cx, cy, s, T):
    # Galileo entry probe: cone heat shield with a parachute
    d.line([(cx - 40 * s, cy - 30 * s), (cx - 110 * s, cy - 190 * s)], fill=OUTL, width=4)
    d.line([(cx + 40 * s, cy - 30 * s), (cx + 110 * s, cy - 190 * s)], fill=OUTL, width=4)
    d.chord([cx - 150 * s, cy - 290 * s, cx + 150 * s, cy - 120 * s], 180, 360, fill=(240, 120, 60), outline=OUTL, width=5)
    d.polygon([(cx - 80 * s, cy), (cx + 80 * s, cy), (cx + 45 * s, cy - 50 * s), (cx - 45 * s, cy - 50 * s)],
              fill=(200, 200, 210), outline=OUTL)
    d.ellipse([cx - 80 * s, cy - 18 * s, cx + 80 * s, cy + 30 * s], fill=(150, 90, 60), outline=OUTL, width=4)

def galileo_props(frame, d, T, sc):
    lt = T - sc["s"]
    sh = (3 * math.sin(T * 30)) if lt > 3.5 else 0
    probe(d, 760 + sh, 1000 + 30 * math.sin(T * 2), 1.0, T)
    if lt > 1.0: top_label(frame, "GALILEO PROBE, 1995", 380, YEL, 62)
    if lt > 3.4:
        l = label("58 MINUTES", 60, WHITE); comp(frame, l, 760 - l.width / 2, 1110)

def metal_props(frame, d, T, sc):
    lt = T - sc["s"]
    for i in range(7):   # silvery droplets
        x = 120 + (i * 151) % 860
        y = (i * 257 - T * 500) % 680 + 560
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=(200, 205, 220), outline=OUTL, width=4)
        d.ellipse([x - 14, y - 16, x - 2, y - 4], fill=WHITE)
    if lt > 1.0: top_label(frame, "LIQUID METAL HYDROGEN", 380, YEL, 58)

def core_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "~24,000 °C", 380, YEL, 80)
    if lt > 3.0:
        l = label("SUN'S SURFACE: ~5,500 °C", 50, WHITE); comp(frame, l, 540 - l.width / 2, 480)

def guru_props(frame, d, T, sc):
    lt = T - sc["s"]
    jupiter(d, 790, 1090, 130, T, face=True)
    if lt > 1.0: top_label(frame, "GURU = JUPITER", 380, YEL, 70)
    if lt > 3.2:
        l = label("THURSDAY = GURUVAR", 54, WHITE); comp(frame, l, 540 - l.width / 2, 470)

def orbiter(d, cx, cy, s):
    d.rectangle([cx - 40 * s, cy - 30 * s, cx + 40 * s, cy + 30 * s], fill=(220, 210, 160), outline=OUTL, width=4)
    d.chord([cx - 90 * s, cy - 150 * s, cx + 90 * s, cy - 10 * s], 0, 180, fill=(235, 235, 240), outline=OUTL, width=4)
    d.line([(cx, cy - 80 * s), (cx, cy - 130 * s)], fill=OUTL, width=4)
    for sx in (-1, 1):
        d.line([(cx + sx * 40 * s, cy), (cx + sx * 150 * s, cy + 40 * s)], fill=OUTL, width=5)
        d.ellipse([cx + sx * 150 * s - 14, cy + 40 * s - 14, cx + sx * 150 * s + 14, cy + 40 * s + 14], fill=(90, 90, 100))

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    jupiter(d, 280, 1060, 170, T, face=False)
    # Europa: icy moon on the right
    d.ellipse([760, 880, 920, 1040], fill=(236, 226, 206), outline=OUTL, width=5)
    for a, b, c, e in ((785, 920, 885, 945), (775, 985, 905, 1005), (815, 895, 850, 1030)):
        d.line([(a, b), (c, e)], fill=(176, 120, 90), width=4)
    l = label("EUROPA", 44, WHITE); comp(frame, l, 840 - l.width / 2, 1050)
    q = ease_out(clamp((lt - 0.5) / 3.0))
    ox, oy = 700 - 320 * q, 960 + 90 * q
    if q < 0.98: orbiter(d, ox, oy, 0.8 - 0.4 * q)
    if lt > 1.0: top_label(frame, "2003: ON PURPOSE", 380, YEL, 66)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="approach", s=4.0, e=11.0, bg_fn=approach_bg, clock="ARRIVAL SPEED", char="kid",
         pos=(540, 1060, 400), rot=fall_rot, props=approach_props, look=(0, 0.6),
         narr="Jupiter's gravity would pull you in at about 200,000 KM/H before you even hit the CLOUDS.",
         n_at=4.2, say="Why is it getting BIGGER?", say_at=7.4, pitch=620, bubble_y=780),
    dict(id="ground", s=11.0, e=18.0, bg_fn=fall_bg("cloud"), clock="BRACE FOR LANDING", char="kid",
         pos=fall_pos(), rot=fall_rot, props=ground_props, look=(0, 0.6),
         narr="Brace for landing... except there's NO GROUND. Jupiter is mostly HYDROGEN and HELIUM gas.",
         n_at=11.2, say="Where's the FLOOR?", say_at=14.6, pitch=620, bubble_y=780),
    dict(id="gravity", s=18.0, e=25.0, bg_fn=fall_bg("cloud", 600), clock="HEAVY", char="kid", state="puff",
         pos=fall_pos(1070, 440, 20), props=gravity_props, look=(0, 0.6),
         narr="Gravity here is about 2.5 TIMES Earth's. A 40 KG kid would feel like 100 KG.",
         n_at=18.2, say="My arms weigh a TON!", say_at=21.6, pitch=620, bubble_y=780),
    dict(id="wind", s=25.0, e=32.0, bg_fn=fall_bg("cloud", 300, 900), clock="STORM ZONE", char="kid",
         pos=lambda T: (540 + 110 * math.sin(T * 2.6), 1070, 420), rot=lambda T: 25 * math.sin(T * 2.6),
         props=wind_props, look=(-0.6, 0),
         narr="Winds blow at about 650 KM/H. That's about TWICE a bullet train's top speed.",
         n_at=25.2, say="Hold my CHAPPAL!", say_at=28.6, pitch=620, bubble_y=780),
    dict(id="spot", s=32.0, e=39.0, bg_fn=fall_bg("cloud", 120), clock="GIANT STORM", char="earth",
         pos=(540, 1170, 260), state=lambda T: T * 12, props=spot_props, look=(0, -0.6),
         narr="And the GREAT RED SPOT is a storm WIDER than our entire EARTH.", n_at=32.2,
         say="I'd fit INSIDE that!", say_at=35.4, pitch=300, bubble_y=960),
    dict(id="galileo", s=39.0, e=46.0, bg_fn=fall_bg("deep", 260), clock="SOMEONE TRIED", char="kid",
         pos=(300, 1080, 400), props=galileo_props, look=(0.6, 0),
         narr="In 1995 NASA's GALILEO probe dived in. It lasted 58 MINUTES before heat and pressure won.",
         n_at=39.2, say="Not even ONE hour!", say_at=42.8, pitch=620, bubble_y=780),
    dict(id="metal", s=46.0, e=53.0, bg_fn=fall_bg("metal", 500), clock="DEEPER", char="kid", state="puff",
         pos=fall_pos(1080, 420, 30), rot=fall_rot, props=metal_props, look=(0.4, 0.3),
         narr="Deeper down, crushing pressure squeezes HYDROGEN into a LIQUID METAL.", n_at=46.2,
         say="Swimming in METAL?!", say_at=49.4, pitch=620, bubble_y=780),
    dict(id="core", s=53.0, e=60.0, bg_fn=fall_bg("core", 200), clock="THE CENTRE", char="sun",
         pos=(540, 1060, 400), props=core_props, look=(0, 0),
         narr="Near the centre it may reach about 24,000 °C. Hotter than the SUN's surface.", n_at=53.2,
         say="Even I'm JEALOUS.", say_at=56.6, pitch=260, bubble_y=840),
    dict(id="guru", s=60.0, e=67.0, bg="night", clock="INDIAN CONNECTION", char="uncle", state="hat",
         pos=(330, 1060, 380), props=guru_props, look=(0.6, -0.3),
         narr="In India, Jupiter is GURU. That's why Thursday is called GURUVAR.", n_at=60.2,
         say="Guru ji, SAVE me!", say_at=63.2, pitch=200, bubble_y=850),
    dict(id="twist", s=67.0, e=74.0, bg="space", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: NASA later crashed Galileo into Jupiter ON PURPOSE, to keep Earth germs off EUROPA.",
         n_at=67.2, say="No GERMS for Europa!", say_at=70.4, pitch=360, bubble_y=760),
    dict(id="outro", s=74.0, e=79.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back(clamp((T - 1.9) / 0.4))
        if p > 0.02: jupiter(d, 540, 1470, 190 * p, T, face=False)

cfg = dict(
    total=79.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU FELL", WHITE)], 140), 720, 0.75, "right"),
        (title([("INTO", WHITE)], 140), 865, 1.05, "left"),
        (title([("JUPITER?", YEL)], 150), 1020, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" take", WHITE)], 100), 470, 0.15),
                      (title([("the plunge?", YEL)], 110), 600, 0.45)],
               row=[("kid", "puff"), ("earth", 1), ("sun", 1), ("uncle", "hat"), ("rocket", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=32.0, drums=False, minor=True), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=60.0, drums=False, minor=True), dict(t0=60.0, t1=66.85, melody=True),
           dict(t0=74.0, t1=79.0, melody=True)],
    drones=[dict(t0=46.2, dur=13.0, g=0.04), dict(t0=67.2, dur=6.5, g=0.05)],
    fx=[("whoosh", 4.6, 0.6), ("wind", 11.2, 0.35, dict(dd=6.5)), ("gasp", 15.0, 0.4), ("rumble", 18.4, 0.4, dict(dd=3.0)),
        ("gale", 25.2, 0.5, dict(dd=6.5)), ("rumble", 32.4, 0.4, dict(dd=4.0)), ("rumble", 42.4, 0.5, dict(dd=3.0)),
        ("powerdown", 44.4, 0.5), ("bubbles", 46.4, 0.3, dict(dd=6.0)), ("rumble", 53.4, 0.6, dict(dd=5.0)),
        ("ding", 61.0, 0.3), ("crash", 70.2, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_fell_into_jupiter")
