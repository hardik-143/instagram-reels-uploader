#!/usr/bin/env python3
"""What if you lived on the ISS for a day? NASA facts & figures: 16 orbits in 24 h, ~90 min per orbit, five miles per
second (~8 km/s, ~28,000 km/h); altitude ~400 km. Gravity at ISS altitude ~90% of surface; crew float because they are
in free fall (BGR / NASA microgravity explainer). Liquids don't settle; crews drink from pouches with straws (BGR).
Astronauts can grow up to ~3% taller, ~5 cm for a 1.8 m person, back to normal after months on Earth (Space.com).
ECLSS Water Recovery System with Brine Processor reached 98% water recovery from urine and sweat (NASA, June 2023).
Microgravity flames are spherical, soot-free and blue (NASA candle flame image); flames run in the Combustion
Integrated Rack (NASA). Twist: the viral 'India on Diwali from space' image is a 2003 NOAA (Chris Elvidge) DMSP colour
composite of city-light growth 1992-2003, not Diwali (Snopes, quoting NASA)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 53.0

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), rot=0):
    spr = draw_char(kind, size, T, 0, False, look, state)
    if rot: spr = spr.rotate(rot, resample=Image.BICUBIC, expand=False)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def module():
    """Inside a space-station module: white padded walls, handrails, cables, a round window."""
    if "module" not in _cache:
        img = E.grad([(0, (200, 210, 224)), (1, (170, 180, 198))], W, H) if hasattr(E, "grad") else None
        img = img.convert("RGBA"); d = ImageDraw.Draw(img)
        for x in range(0, W, 180):
            d.rectangle([x + 6, 160, x + 174, H - 40], fill=(226, 230, 238), outline=(150, 160, 178), width=4)
            for y in range(240, H - 80, 260):
                d.rectangle([x + 40, y, x + 140, y + 60], fill=(206, 212, 224), outline=(160, 170, 186), width=3)
        d.rectangle([0, 120, W, 175], fill=(120, 130, 150))
        d.rectangle([0, H - 60, W, H], fill=(120, 130, 150))
        for y in (560, 1380):
            d.rounded_rectangle([60, y, 1020, y + 26], radius=13, fill=(250, 200, 60), outline=OUTL, width=4)
        rng = np.random.default_rng(5)
        for k in range(10):
            x = rng.uniform(40, 1040); y = rng.uniform(600, 1300)
            d.rounded_rectangle([x, y, x + 70, y + 40], radius=8, fill=tuple(int(c) for c in rng.integers(90, 220, 3)),
                                outline=OUTL, width=3)
        _cache["module"] = img
    return _cache["module"]

def window(frame, d, cx, cy, r, T, day=1.0):
    """Round porthole; day in 0..1 blends from night (city lights) to day (blue Earth, Sun)."""
    d.ellipse([cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22], fill=(140, 150, 170), outline=OUTL, width=8)
    S = 2 * r
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    sky = tuple(int(a * (1 - day) + b * day) for a, b in zip((8, 10, 30), (20, 30, 80)))
    ld.rectangle([0, 0, S, S], fill=sky)
    ex = tuple(int(a * (1 - day) + b * day) for a, b in zip((20, 30, 60), (60, 140, 230)))
    ld.ellipse([-S * 0.6, S * 0.55, S * 1.6, S * 2.4], fill=ex)
    if day > 0.6:
        ld.ellipse([S * 0.62, S * 0.14, S * 0.8, S * 0.32], fill=(255, 230, 120))
    if day < 0.5:
        for k in range(8):
            x = S * 0.15 + k * S * 0.1; y = S * 0.72 + (k % 3) * 10
            ld.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 220, 120))
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S - 1, S - 1], fill=255)
    L.putalpha(m)
    comp(frame, L, cx - r, cy - r)

def iss(d, x, y, s=1.0):
    d.rectangle([x - 130 * s, y - 8 * s, x + 130 * s, y + 8 * s], fill=(190, 190, 200), outline=OUTL, width=3)
    for dx in (-110, -70, 70, 110):
        d.rectangle([x + (dx - 16) * s, y - 70 * s, x + (dx + 16) * s, y + 70 * s], fill=(60, 90, 170),
                    outline=OUTL, width=3)
    d.rounded_rectangle([x - 40 * s, y - 20 * s, x + 40 * s, y + 20 * s], radius=10 * s, fill=WHITE, outline=OUTL,
                        width=3)

# ---------------------------------------------------------------- props
def orbit_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "earth", 540, 1150, 520, T, state=T * 0.2)
    a = lt * 1.1
    rx, ry = 430, 150
    x = 540 + rx * math.cos(a); y = 1150 + ry * math.sin(a) - 40
    d.ellipse([540 - rx, 1150 - ry - 40, 540 + rx, 1150 + ry - 40], outline=(255, 255, 255, 120), width=3)
    if math.sin(a) < 0:   # behind Earth -> redraw Earth on top
        iss(d, x, y, 0.6); mini(frame, "earth", 540, 1150, 520, T, state=T * 0.2)
    else:
        iss(d, x, y, 0.6)
    if lt > 0.5:
        top_label(frame, "28,000 KM/H", 380, YEL, 80)

def sunrise_props(frame, d, T, sc):
    lt = T - sc["s"]
    day = 0.5 + 0.5 * math.sin(lt * 2.4)
    window(frame, d, 620, 1040, 190, T, day)
    n = min(16, 1 + int(lt * 2.6))
    if lt > 0.3:
        top_label(frame, f"SUNRISE #{n}", 380, YEL, 74)

def float_pos(T):
    lt = T - 18.0
    return (540 + 120 * math.sin(lt * 0.9), 1000 + 60 * math.sin(lt * 1.3), 380)

def float_props(frame, d, T, sc):
    lt = T - sc["s"]
    # floating crumbs and a spoon
    for k in range(5):
        x = 160 + k * 190 + 30 * math.sin(T + k); y = 700 + 40 * math.sin(T * 1.2 + k * 2)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(250, 200, 120), outline=OUTL, width=3)
    if lt > 0.5:
        top_label(frame, "GRAVITY HERE: ~90%", 380, YEL, 70)

def chai_props(frame, d, T, sc):
    lt = T - sc["s"]
    # floating blobs of chai
    for k in range(4):
        x = 230 + k * 210 + 40 * math.sin(T * 1.4 + k); y = 920 + 60 * math.sin(T * 1.1 + k * 1.7)
        r = 38 + 10 * math.sin(T * 3 + k)
        d.ellipse([x - r, y - r * 0.9, x + r, y + r * 0.9], fill=(196, 140, 90), outline=OUTL, width=5)
        d.ellipse([x - r * 0.5, y - r * 0.6, x - r * 0.15, y - r * 0.3], fill=(240, 210, 170))
    # drink pouch with a straw
    if lt > 3.0:
        px, py = 820, 1180
        d.rounded_rectangle([px - 70, py - 90, px + 70, py + 90], radius=20, fill=(230, 236, 246), outline=OUTL, width=6)
        d.rectangle([px - 50, py - 10, px + 50, py + 70], fill=(196, 140, 90))
        d.line([(px + 20, py - 90), (px + 40, py - 170)], fill=(240, 80, 80), width=12)
    if lt > 0.5:
        top_label(frame, "NO POURING", 380, YEL, 80)

def tall_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 1.0) / 2.0))
    # height chart on the right
    d.rectangle([840, 700, 960, 1400], fill=WHITE, outline=OUTL, width=6)
    for k in range(15):
        y = 1380 - k * 46
        d.line([(840, y), (880 if k % 2 else 910, y)], fill=OUTL, width=4)
    top = 860 - 70 * g
    d.line([(760, top), (960, top)], fill=(230, 40, 50), width=8)
    if lt > 0.5:
        top_label(frame, "UP TO +5 CM", 380, YEL, 80)

def tall_pos(T):
    lt = T - 32.0
    g = ease_out(clamp((lt - 1.0) / 2.0))
    return (500, 1080 - 30 * g, int(460 + 40 * g))

def water_props(frame, d, T, sc):
    lt = T - sc["s"]
    # recycling machine with a pipe feeding a pouch
    d.rounded_rectangle([660, 820, 1000, 1300], radius=24, fill=(150, 160, 180), outline=OUTL, width=8)
    d.rectangle([700, 870, 960, 960], fill=(30, 40, 60))
    pct = int(98 * clamp(lt / 2.5))
    l = label(f"{pct}%", 64, (120, 255, 160)); comp(frame, l, 830 - l.width / 2, 870)
    for k in range(3):
        y = 1000 + ((lt * 120 + k * 60) % 180)
        d.ellipse([820, y, 850, y + 40], fill=(120, 190, 255), outline=OUTL, width=3)
    if lt > 0.5:
        top_label(frame, "SWEAT + PEE = WATER", 380, YEL, 66)

def diya_props(frame, d, T, sc):
    lt = T - sc["s"]
    # sealed experiment box
    d.rounded_rectangle([250, 820, 830, 1340], radius=30, fill=(40, 46, 70), outline=OUTL, width=10)
    d.rounded_rectangle([290, 860, 790, 1300], radius=20, fill=(20, 22, 40))
    # clay diya
    d.chord([400, 1150, 680, 1290], 0, 180, fill=(196, 100, 50), outline=OUTL, width=6)
    d.ellipse([400, 1180, 680, 1230], fill=(170, 80, 40), outline=OUTL, width=6)
    # on Earth: teardrop yellow flame; in space: round blue flame
    q = ease_out(clamp((lt - 2.2) / 0.8))
    fx, fy = 540, 1120
    if q < 1:
        a = int(255 * (1 - q))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.polygon([(fx, fy - 150), (fx + 40, fy - 30), (fx, fy + 10), (fx - 40, fy - 30)], fill=(255, 190, 50, a))
        frame.alpha_composite(ov)
    if q > 0:
        r = 60 * q
        for k, c in enumerate(((60, 120, 255), (120, 180, 255), (210, 230, 255))):
            rr = r * (1 - k * 0.3)
            d.ellipse([fx - rr, fy - 40 - rr, fx + rr, fy - 40 + rr], fill=c)
    if lt > 0.5:
        top_label(frame, "EARTH" if lt < 2.4 else "SPACE: ROUND + BLUE", 380, YEL, 70)

def photo_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a phone showing a colourful 'India from space' map with a FAKE stamp
    px, py = 300, 830
    d.rounded_rectangle([px - 170, py - 10, px + 170, py + 600], radius=40, fill=(30, 30, 40), outline=OUTL, width=8)
    d.rectangle([px - 145, py + 40, px + 145, py + 540], fill=(6, 8, 24))
    rng = np.random.default_rng(9)
    cols = [(255, 255, 255), (80, 140, 255), (80, 220, 120), (255, 80, 80)]
    for k in range(140):
        x = px + rng.normal(0, 60); y = py + 260 + rng.normal(0, 110)
        if abs(x - px) < 140 and py + 50 < y < py + 530:
            c = cols[int(rng.integers(0, 4))]
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=c)
    if lt > 2.2:
        st = label("NOT DIWALI", 54, (255, 70, 70))
        st = st.rotate(18, resample=Image.BICUBIC, expand=True)
        comp(frame, st, px - st.width / 2, py + 200)
    if lt > 0.5:
        top_label(frame, "THE VIRAL PHOTO", 380, YEL, 74)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="orbit", s=4.0, e=11.0, bg="space", clock="06:00 · WAKE UP",
         props=orbit_props,
         narr="Your new home flies about 400 KM up and circles Earth every 90 MINUTES.", n_at=4.2, narr_y=1560),
    dict(id="sunrise", s=11.0, e=18.0, bg_fn=lambda T: module(), clock="07:30 · BREAKFAST", char="kid",
         pos=(210, 1260, 300), props=sunrise_props, look=(0.6, -0.4),
         narr="So you get about 16 SUNRISES and 16 SUNSETS every single day.", n_at=11.2, narr_y=1560,
         say="Good morning... AGAIN?!", say_at=14.2, pitch=420),
    dict(id="float", s=18.0, e=25.0, bg_fn=lambda T: module(), clock="09:00 · COMMUTE", char="kid",
         pos=float_pos, rot=lambda T: 25 * math.sin(T * 0.8), props=float_props, look=(0, 0.3),
         narr="You float, but gravity is still about 90% here. You're FALLING around Earth.", n_at=18.2,
         narr_y=1560, say="I'm falling... SIDEWAYS!", say_at=21.4, pitch=420),
    dict(id="chai", s=25.0, e=32.0, bg_fn=lambda T: module(), clock="11:00 · CHAI BREAK", char="chai",
         pos=(330, 1180, 360), props=chai_props, look=(0.4, -0.4),
         narr="Chai won't pour. Liquids float as BLOBS, so you sip from a POUCH.", n_at=25.2, narr_y=1560,
         say="Catch me if you CAN!", say_at=28.2, pitch=460),
    dict(id="tall", s=32.0, e=39.0, bg_fn=lambda T: module(), clock="14:00 · HEALTH CHECK", char="kid",
         pos=tall_pos, props=tall_props, look=(0.5, -0.5),
         narr="Your spine stretches out. Astronauts can grow up to 3% TALLER.", n_at=32.2, narr_y=1560,
         say="Finally, 5 CM TALLER!", say_at=35.2, pitch=420),
    dict(id="water", s=39.0, e=46.0, bg_fn=lambda T: module(), clock="17:00 · WATER TIME", char="kid",
         pos=(330, 1150, 360), props=water_props, look=(0.6, -0.2),
         narr="Your drinking water? NASA recycles 98% of it, even from SWEAT and URINE.", n_at=39.2,
         narr_y=1560, say="Ewww... but it's CLEAN?!", say_at=42.4, pitch=420),
    dict(id="diya", s=46.0, e=TW, bg_fn=lambda T: module(), clock="19:00 · DIWALI", props=diya_props,
         narr="Diwali diya? Flames are lit only in test boxes, and they burn ROUND and BLUE.", n_at=46.2,
         narr_y=1560),
    dict(id="twist", s=TW, e=60.0, bg="night", clock="PLOT TWIST", char="uncle", pos=(780, 1100, 380),
         props=photo_props, twist=True, look=(-0.6, 0.1),
         narr="Twist: that viral 'India on Diwali from space' photo is a 2003 city-lights MAP.", n_at=TW + 0.2,
         narr_y=1560, say="But I forwarded it TEN times!", say_at=TW + 3.2, pitch=150),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        iss(d, 540 + 30 * math.sin(T * 1.5), 1400 + 12 * math.sin(T * 2.5), 1.4 * min(p, 1.2))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED ON THE", WHITE)], 110), 770, 0.75, "right"),
        (title([("ISS FOR A DAY?", YEL)], 130), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" move", WHITE)], 100), 470, 0.15),
                      (title([("to the ISS?", YEL)], 96), 600, 0.45)],
               row=[("rocket", 1), ("earth", 1), ("kid", 1), ("chai", 1), ("diya", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, drums=False, melody=True),
           dict(t0=11.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, melody=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=4.0, dur=7.0, g=0.25)],
    fx=[("whoosh", 6.0, 0.4), ("ding", 12.0, 0.25), ("ding", 13.4, 0.25), ("ding", 15.0, 0.25),
        ("bubbles", 25.3, 0.3, dict(dd=6.0)), ("pop", 28.5, 0.3), ("pop", 35.0, 0.4),
        ("bubbles", 39.6, 0.25, dict(dd=4.0)), ("ding", 41.6, 0.35), ("click", 47.0, 0.4), ("pop", 48.4, 0.5)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_on_the_iss")
