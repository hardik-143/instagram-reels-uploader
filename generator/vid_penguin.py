#!/usr/bin/env python3
"""What if you were an emperor penguin for a day? Facts: tallest + heaviest penguin, up to ~1.2 m and ~45 kg (WHOI
'Fascinating facts about emperor penguins'; Animal Diversity Web 101-132 cm, 25-45 kg). Breeds through the Antarctic
winter, temperatures down to about -50 C and winds up to 200 km/h (WWF-UK top 10 facts; WHOI). Female lays one egg and
passes it to the male, then goes to sea to feed; the male balances it on his feet under a fold of skin for 65-75 days
(WWF-UK; Australian Antarctic Division 'Breeding cycle'). By the time the chick hatches he has fasted for about 4 months
and lost nearly half his body mass (AAD; WWF-UK; ADW says ~40%). Huddles of 5,000 or more shuffle so each bird takes a
turn on the cold outside (WWF-UK; ADW 'as large as 5,000 or 6,000'). Deepest dive by a bird 564 m (Guinness World
Records; AAD 565 m); most dives 100-200 m (AAD). Qutub Minar 72.5 m, so 564 m = ~7.8 Qutub Minars. Twist: if the chick
hatches before the female returns, the male feeds it a nutrient-rich milky secretion from his oesophagus (ADW)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
ICE = (120, 190, 255)
SNOW = (246, 250, 255)
EGG = (250, 244, 228)

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

def snowfall(d, T, n=45, seed=5, speed=120, slant=0.0):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        x = (x0 + 25 * math.sin(T * 1.3 + k) + slant * T * 400) % W
        y = (y0 + T * speed * (0.6 + (k % 5) * 0.15)) % H
        r = 4 + (k % 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

def mini_peng(d, x, y, s=1.0, ph=0.0):
    """Small background penguin for huddles."""
    w, h = 38 * s, 70 * s
    y += 3 * math.sin(ph)
    d.ellipse([x - w, y - h, x + w, y + h], fill=(30, 34, 48), outline=OUTL, width=3)
    d.ellipse([x - w * 0.62, y - h * 0.55, x + w * 0.62, y + h * 0.95], fill=(250, 248, 240))
    d.ellipse([x - w * 0.55, y - h * 0.95, x - w * 0.05, y - h * 0.55], fill=(255, 196, 60))
    d.ellipse([x - w * 0.3, y - h * 0.8, x - w * 0.12, y - h * 0.62], fill=(20, 20, 30))
    d.polygon([(x - w * 0.95, y - h * 0.65), (x - w * 1.35, y - h * 0.58), (x - w * 0.95, y - h * 0.52)],
              fill=(240, 120, 60))

# ---------------------------------------------------------------- backgrounds
_cache = {}
def night_bg(T):
    if "night" not in _cache:
        img = E.grad([(0, (10, 18, 50)), (0.6, (40, 60, 110)), (1, (70, 90, 140))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img); rng = np.random.default_rng(3)
        for k in range(90):
            x, y = rng.uniform(0, W), rng.uniform(0, 1100); r = rng.uniform(1, 3)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
        for k in range(3):
            pts = [(x, 620 + k * 40 + 60 * math.sin(x / 160 + k)) for x in range(0, W + 40, 40)]
            d.line(pts, fill=(90, 220, 160), width=18 - k * 4)
        d.rectangle([0, 1330, W, H], fill=(120, 140, 185))
        d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
        _cache["night"] = img
    img = _cache["night"].copy(); d = ImageDraw.Draw(img)
    snowfall(d, T, n=40, slant=0.6)
    return img

def ice_bg(T):
    if "day" not in _cache:
        img = E.grad([(0, (150, 200, 250)), (0.65, (226, 240, 255)), (1, (226, 240, 255))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.polygon([(0, 1100), (260, 800), (520, 1100)], fill=(200, 215, 240), outline=OUTL)
        d.polygon([(560, 1100), (850, 760), (1080, 1100)], fill=(190, 205, 235), outline=OUTL)
        d.rectangle([0, 1100, W, H], fill=(214, 230, 250))
        d.line([(0, 1100), (W, 1100)], fill=OUTL, width=6)
        _cache["day"] = img
    return _cache["day"]

def deep_bg(T):
    if "deep" not in _cache:
        img = E.grad([(0, (70, 160, 230)), (0.35, (20, 80, 150)), (1, (4, 14, 40))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 120], fill=(230, 242, 255))
        d.line([(0, 120), (W, 120)], fill=OUTL, width=6)
        _cache["deep"] = img
    img = _cache["deep"].copy(); d = ImageDraw.Draw(img)
    for k in range(14):
        ph = (T * 0.25 + k / 14) % 1
        x = 120 + (k * 73) % 860; y = 1800 - 1600 * ph
        r = 6 + k % 4
        d.ellipse([x - r, y - r, x + r, y + r], outline=(200, 230, 255), width=3)
    return img

# ---------------------------------------------------------------- props
def therm(d, x, frac, col=ICE, top=820):
    d.rounded_rectangle([x - 36, top, x + 36, 1220], radius=36, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 66, 1180, x + 66, 1310], fill=col, outline=OUTL, width=8)
    lvl = 1210 - (1210 - top - 30) * frac
    d.rectangle([x - 18, lvl, x + 18, 1210], fill=col)

def cold_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.6) / 2.4))
    therm(d, 880, 0.85 * (1 - g) + 0.05)
    if lt > 0.5:
        top_label(frame, f"{-int(50 * g)} °C", 380, YEL, 110)
    if lt > 2.5:
        at_label(frame, "200 KM/H WIND", 540, 560, WHITE, 60)

def size_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.4) / 1.6))
    # measuring pole beside the penguin
    x, base = 820, 1330
    top = base - 600 * g
    d.rectangle([x - 18, top, x + 18, base], fill=(255, 210, 90), outline=OUTL, width=5)
    for i in range(1, 7):
        y = base - 100 * i
        if y > top: d.line([(x - 18, y), (x + 4, y)], fill=OUTL, width=4)
    if lt > 0.5:
        top_label(frame, "UP TO 1.2 M", 380, YEL, 100)
    if lt > 2.0:
        at_label(frame, "45 KG", 170, 1000, WHITE, 64)

def egg(d, x, y, s=1.0, wob=0.0):
    w, h = 46 * s, 58 * s
    d.ellipse([x - w + wob, y - h, x + w + wob, y + h], fill=EGG, outline=OUTL, width=5)

def egg_props(frame, d, T, sc):
    lt = T - sc["s"]
    # mum on the right walks off to the sea; the egg slides left to dad
    q = clamp((lt - 1.0) / 1.5)
    ex = 760 - 330 * ease_out(q); ey = 1290
    egg(d, ex, ey, 0.9, 4 * math.sin(T * 8) * (1 - q))
    mx = 840 + 400 * clamp((lt - 3.0) / 3.0)
    mini_peng(d, mx, 1220, 2.0, T * 6)
    if lt > 0.5:
        top_label(frame, "ONE EGG", 380, YEL, 110)
    if lt > 3.5:
        at_label(frame, "MUM: OFF TO SEA", 760, 990, WHITE, 52)

def feet_props_after(frame, d, T, sc):
    lt = T - sc["s"]
    egg(d, 540, 1285, 0.85, 3 * math.sin(T * 3))

def feet_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.5:
        days = min(75, int(75 * clamp((lt - 0.8) / 4.0)))
        top_label(frame, f"DAY {days}", 380, YEL, 110)

def fast_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.8) / 3.0))
    # weight bar shrinking to half
    x0, y0 = 160, 560
    full = 760
    d.rounded_rectangle([x0, y0, x0 + full, y0 + 70], radius=30, fill=(255, 255, 255), outline=OUTL, width=6)
    d.rounded_rectangle([x0 + 6, y0 + 6, x0 + 6 + (full - 12) * (1 - 0.5 * g), y0 + 64], radius=26,
                        fill=(240, 110, 90))
    if lt > 0.5:
        top_label(frame, "0 MEALS: 4 MONTHS", 380, YEL, 76)
    if lt > 3.2:
        at_label(frame, "WEIGHT: -HALF", 540, 690, WHITE, 56)

def huddle_props(frame, d, T, sc):
    lt = T - sc["s"]
    # slowly rotating ring of penguins around the hero
    n = 16
    for k in range(n):
        a = 2 * math.pi * k / n + lt * 0.35
        x = 540 + 420 * math.cos(a); y = 1170 + 120 * math.sin(a)
        if math.sin(a) < 0:
            mini_peng(d, x, y, 1.5, T * 5 + k)
    if lt > 0.5:
        top_label(frame, "5,000+ IN A HUDDLE", 380, YEL, 76)

def huddle_after(frame, d, T, sc):
    lt = T - sc["s"]
    n = 16
    for k in range(n):
        a = 2 * math.pi * k / n + lt * 0.35
        x = 540 + 420 * math.cos(a); y = 1170 + 120 * math.sin(a)
        if math.sin(a) >= 0:
            mini_peng(d, x, y, 1.7, T * 5 + k)

def dive_pos(T):
    lt = T - 46.0
    q = ease_out(clamp((lt - 0.3) / 4.0))
    return (330, 760 + 380 * q, 360)

def dive_props(frame, d, T, sc):
    lt = T - sc["s"]
    # stack of Qutub-Minar-like tapered towers, scale bar on the right
    x = 850
    g = clamp((lt - 0.6) / 3.5)
    seg = 130
    for i in range(8):
        if i / 8 > g: break
        top = 340 + i * seg
        frac = 0.8 if i == 7 else 1.0
        h = seg * frac - 8
        d.polygon([(x - 46, top + h), (x + 46, top + h), (x + 32, top), (x - 32, top)], fill=(190, 110, 80),
                  outline=OUTL)
        for b in (0.33, 0.66):
            yy = top + h * b
            d.line([(x - 40, yy), (x + 40, yy)], fill=(120, 60, 40), width=5)
    if lt > 0.5:
        at_label(frame, "564 M DEEP", 380, 420, YEL, 96)
    if lt > 3.0:
        at_label(frame, "~8 QUTUB MINARS", 380, 530, WHITE, 52)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # fluffy grey chick beside dad
    cx, cy = 760, 1230
    b = 4 * math.sin(T * 5)
    d.ellipse([cx - 95, cy - 120 + b, cx + 95, cy + 100], fill=(170, 172, 180), outline=OUTL, width=6)
    d.ellipse([cx - 70, cy - 175 + b, cx + 70, cy - 40 + b], fill=(30, 34, 48), outline=OUTL, width=5)
    d.ellipse([cx - 52, cy - 140 + b, cx + 52, cy - 60 + b], fill=WHITE)
    for ex in (cx - 22, cx + 22):
        d.ellipse([ex - 10, cy - 115 + b, ex + 10, cy - 95 + b], fill=(20, 20, 30))
    d.polygon([(cx - 12, cy - 88 + b), (cx + 12, cy - 88 + b), (cx, cy - 70 + b)], fill=(240, 120, 60))
    if lt > 1.5:
        # little milk droplets
        for k in range(3):
            ph = (lt * 0.8 + k / 3) % 1
            x = 600 + 120 * ph; y = 1030 - 40 * math.sin(ph * math.pi)
            d.ellipse([x - 12, y - 14, x + 12, y + 14], fill=(255, 252, 235), outline=OUTL, width=3)
    if lt > 0.5:
        top_label(frame, "PAPA MILK", 380, YEL, 110)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="cold", s=4.0, e=11.0, bg_fn=night_bg, clock="ANTARCTIC WINTER", char="penguin",
         pos=(400, 1110, 520), props=cold_props, look=(0.6, -0.3),
         narr="You breed in Antarctic WINTER: down to -50 °C, with winds up to 200 KM/H.", n_at=4.2, narr_y=1560,
         say="Perfect weather!", say_at=7.4, pitch=380),
    dict(id="size", s=11.0, e=18.0, bg_fn=ice_bg, clock="BIGGEST PENGUIN", char="penguin",
         pos=(470, 1080, 520), props=size_props, look=(0.5, -0.2),
         narr="You're the BIGGEST penguin alive: up to 1.2 M tall and 45 KG.", n_at=11.2, narr_y=1560,
         say="Emperor, not KING!", say_at=14.2, pitch=380),
    dict(id="egg", s=18.0, e=25.0, bg_fn=ice_bg, clock="MAY: EGG DAY", char="penguin",
         pos=(300, 1110, 460), props=egg_props, look=(0.7, 0.3),
         narr="Mum lays ONE egg, hands it to you, then walks off to the sea to eat.", n_at=18.2, narr_y=1560,
         say="Don't DROP it!", say_at=21.6, pitch=380),
    dict(id="feet", s=25.0, e=32.0, bg_fn=night_bg, clock="EGG DUTY", char="penguin",
         pos=(540, 1030, 520), props=feet_props, props_after=feet_props_after, look=(0, 0.6),
         narr="You balance it on your FEET, under a warm skin flap, for 65-75 DAYS.", n_at=25.2, narr_y=1560,
         say="No walking. Only SHUFFLING.", say_at=28.4, pitch=380),
    dict(id="fast", s=32.0, e=39.0, bg_fn=night_bg, clock="DINNER?", char="penguin",
         pos=(540, 1100, 520), props=fast_props, look=(0, -0.3),
         narr="You eat NOTHING for about 4 MONTHS and lose nearly HALF your weight.", n_at=32.2, narr_y=1560,
         say="I can smell FISH...", say_at=35.4, pitch=380),
    dict(id="huddle", s=39.0, e=46.0, bg_fn=night_bg, clock="TEAMWORK", char="penguin",
         pos=(540, 1120, 440), props=huddle_props, props_after=huddle_after, look=(0, -0.2),
         narr="5,000+ dads HUDDLE and keep shuffling, so everyone takes a turn on the cold EDGE.",
         n_at=39.2, narr_y=1560, say="Your turn outside!", say_at=42.4, pitch=380),
    dict(id="dive", s=46.0, e=TW, bg_fn=deep_bg, clock="FINALLY: FOOD", char="penguin", pos=dive_pos,
         rot=-25, props=dive_props, look=(0.3, 0.6),
         narr="Then dinner: you can dive 564 M down, deeper than nearly 8 QUTUB MINARS.", n_at=46.2,
         narr_y=1560, say="FISH buffet!", say_at=50.0, pitch=380),
    dict(id="twist", s=TW, e=61.0, bg_fn=ice_bg, clock="PLOT TWIST", props=twist_props, twist=True,
         char="penguin", pos=(360, 1110, 460), look=(0.6, 0.1),
         narr="Twist: if the chick hatches before Mum is back, Dad feeds it MILKY goo from his throat.",
         n_at=TW + 0.2, narr_y=1560, say="Papa makes MILK?!", say_at=TW + 3.6, pitch=380),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.15)
        mini_peng(d, 540, 1540, 3.0 * p, T * 5)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU WERE AN", WHITE)], 120), 770, 0.75, "right"),
        (title([("EMPEROR PENGUIN?", YEL)], 120), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Could ", WHITE), ("YOU", YEL), (" skip food", WHITE)], 100), 470, 0.15),
                      (title([("for 4 months?", YEL)], 96), 600, 0.45)],
               row=[("penguin", 1), ("kid", 1), ("fish", 1), ("cloud", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, drums=False, minor=True),
           dict(t0=18.0, t1=32.0, melody=True), dict(t0=32.0, t1=46.0, drums=False, minor=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=66.0, melody=True)],
    drones=[dict(t0=4.0, dur=14.0, g=0.22)],
    fx=[("wind", 4.3, 0.35, dict(dd=6.5)), ("gale", 6.5, 0.2, dict(dd=4.0)), ("pop", 19.2, 0.3),
        ("wind", 25.4, 0.2, dict(dd=6.0)), ("tick", 29.0, 0.2), ("wind", 39.3, 0.2, dict(dd=6.0)),
        ("splash", 46.2, 0.35), ("underwater", 46.6, 0.25, dict(dd=6.0)), ("bubbles", 48.0, 0.2),
        ("pop", 54.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_were_an_emperor_penguin")
