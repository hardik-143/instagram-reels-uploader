#!/usr/bin/env python3
"""What if you slept in an igloo? Facts: Arctic winter nights can reach about -45 C outside; with body heat alone an igloo's
inside can range from -7 to 16 C (Wikipedia 'Igloo', 'igloo effect'); snow is up to 95% trapped air, which makes it an
insulator (Mental Floss, 'How do igloos keep people warm'); blocks laid in a rising spiral into a catenary-like dome, no
frame needed; the low entrance acts as a cold trap because cold air sinks, and the sleeping platform is raised to sit in
the warmer air; a lamp (qulliq) or body heat melts the inner walls slightly and they refreeze into an ice layer that
strengthens the igloo (Wikipedia 'Igloo'). Gulmarg, Kashmir: an igloo cafe built Dec 2021-Feb 2022 by Hotel Kolahoi Green
Heights, 11.43 m tall, 13.56 m wide, 40 seats, claimed as the world's largest (VOA Learning English, 24 Feb 2022).
Twist: the Inuit word 'iglu' means a house of any material; snow houses are 'igluvijaq' (Wikipedia 'Igloo')."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
ICE = (120, 190, 255)
SNOW = (246, 250, 255)
BLOCK = (205, 222, 245)

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

def snowfall(d, T, n=45, seed=5, speed=120, top=0):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        x = (x0 + 25 * math.sin(T * 1.3 + k)) % W
        y = top + (y0 + T * speed * (0.6 + (k % 5) * 0.15)) % (H - top)
        r = 4 + (k % 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

def igloo(d, cx, base, r, rows=6, frac=1.0, tunnel=True):
    """Snow-block dome. frac < 1 builds it row by row from the bottom."""
    h = r * 0.95
    n_rows = max(0, int(math.ceil(rows * frac)))
    if tunnel:
        d.rounded_rectangle([cx + r * 0.45, base - r * 0.42, cx + r * 1.15, base], radius=int(r * 0.2), fill=SNOW,
                            outline=OUTL, width=6)
        d.ellipse([cx + r * 0.95, base - r * 0.32, cx + r * 1.12, base], fill=(40, 50, 80))
    # dome clipped by rows
    top_y = base - h * (n_rows / rows)
    d.pieslice([cx - r, base - h, cx + r, base + h], 180, 360, fill=SNOW, outline=OUTL, width=7) if frac >= 1 else None
    if frac < 1:
        for i in range(n_rows):
            y0 = base - h * (i + 1) / rows; y1 = base - h * i / rows
            w0 = r * math.sqrt(max(0, 1 - ((base - y0) / h) ** 2))
            w1 = r * math.sqrt(max(0, 1 - ((base - y1) / h) ** 2))
            d.polygon([(cx - w1, y1), (cx + w1, y1), (cx + w0, y0), (cx - w0, y0)], fill=SNOW, outline=OUTL)
    # block lines
    for i in range(1, min(n_rows, rows)):
        y = base - h * i / rows
        w = r * math.sqrt(max(0, 1 - (i / rows) ** 2))
        d.line([(cx - w + 4, y), (cx + w - 4, y)], fill=(170, 195, 230), width=4)
    for i in range(min(n_rows, rows)):
        y0 = base - h * (i + 1) / rows; y1 = base - h * i / rows
        w = r * math.sqrt(max(0, 1 - ((i + 0.5) / rows) ** 2))
        nb = max(2, int(6 - i * 0.8))
        for j in range(1, nb):
            x = cx - w + 2 * w * (j + 0.5 * (i % 2)) / nb
            if abs(x - cx) < w - 10:
                d.line([(x, y0 + 4), (x, y1 - 4)], fill=(170, 195, 230), width=4)

def section(frame, d, T, cx=470, base=1300, r=310, inner_col=(255, 200, 120)):
    """Cut-away igloo: thick snow shell, low tunnel on the right, raised bed on the left."""
    h = r * 0.95; t = 46
    d.pieslice([cx - r, base - h, cx + r, base + h], 180, 360, fill=SNOW, outline=OUTL, width=7)
    d.pieslice([cx - r + t, base - h + t, cx + r - t, base + h - t], 180, 360, fill=inner_col)
    # tunnel dug lower than the floor
    d.rectangle([cx + r - t - 10, base, cx + r + 170, base + 110], fill=inner_col)
    d.line([(cx + r - t - 10, base + 110), (cx + r + 170, base + 110)], fill=OUTL, width=6)
    d.line([(cx + r, base), (cx + r + 170, base)], fill=OUTL, width=6)
    d.rectangle([cx - r + t, base, cx + r - t - 10, base + 110], fill=SNOW)
    # raised sleeping platform
    d.rectangle([cx - r + t, base - 110, cx + 40, base], fill=BLOCK, outline=OUTL, width=6)
    d.rectangle([cx - r + t + 20, base - 140, cx + 20, base - 110], fill=(240, 120, 110), outline=OUTL, width=5)
    d.line([(0, base), (cx - r, base)], fill=OUTL, width=6)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def night_bg(T):
    if "night" not in _cache:
        img = E.grad([(0, (10, 18, 50)), (0.6, (40, 60, 110)), (1, (70, 90, 140))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img); rng = np.random.default_rng(3)
        for k in range(90):
            x, y = rng.uniform(0, W), rng.uniform(0, 1100); r = rng.uniform(1, 3)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
        # aurora
        for k in range(3):
            pts = [(x, 620 + k * 40 + 60 * math.sin(x / 160 + k)) for x in range(0, W + 40, 40)]
            d.line(pts, fill=(90, 220, 160), width=18 - k * 4)
        d.rectangle([0, 1330, W, H], fill=(120, 140, 185))
        d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
        _cache["night"] = img
    img = _cache["night"].copy(); d = ImageDraw.Draw(img)
    snowfall(d, T, n=35)
    return img

def day_snow_bg(T):
    if "day" not in _cache:
        img = E.grad([(0, (150, 200, 250)), (0.65, (226, 240, 255)), (1, (226, 240, 255))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.polygon([(0, 1100), (260, 760), (520, 1100)], fill=(200, 215, 240), outline=OUTL)
        d.polygon([(380, 1100), (720, 700), (1080, 1100)], fill=(190, 205, 235), outline=OUTL)
        d.polygon([(200, 860), (260, 760), (320, 860)], fill=WHITE)
        d.polygon([(640, 795), (720, 700), (800, 795)], fill=WHITE)
        d.rectangle([0, 1100, W, H], fill=(150, 172, 215))
        d.line([(0, 1100), (W, 1100)], fill=OUTL, width=6)
        _cache["day"] = img
    return _cache["day"]

# ---------------------------------------------------------------- props
def therm(d, x, frac, col=ICE, top=820):
    d.rounded_rectangle([x - 36, top, x + 36, 1220], radius=36, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 66, 1180, x + 66, 1310], fill=col, outline=OUTL, width=8)
    lvl = 1210 - (1210 - top - 30) * frac
    d.rectangle([x - 18, lvl, x + 18, 1210], fill=col)

def cold_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.6) / 2.4))
    therm(d, 860, 0.85 * (1 - g) + 0.05)
    if lt > 0.5:
        top_label(frame, f"{-int(45 * g)} °C", 380, YEL, 110)

def air_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a giant snow block with air bubbles inside
    g = min(ease_back(clamp((lt - 0.3) / 0.6)), 1.1)
    bx, by, s = 760, 1060, 300 * g
    d.rounded_rectangle([bx - s / 2, by - s / 2, bx + s / 2, by + s / 2], radius=24, fill=BLOCK, outline=OUTL, width=7)
    rng = np.random.default_rng(9)
    for k in range(int(24 * g)):
        x = bx + rng.uniform(-0.42, 0.42) * s; y = by + rng.uniform(-0.42, 0.42) * s
        r = (8 + rng.uniform(0, 10)) * (1 + 0.15 * math.sin(T * 4 + k))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255), outline=(150, 175, 215), width=3)
    if lt > 0.5:
        top_label(frame, "95% AIR", 380, YEL, 110)

def build_props(frame, d, T, sc):
    lt = T - sc["s"]
    frac = clamp((lt - 0.4) / 4.0)
    igloo(d, 620, 1100, 250, rows=6, frac=max(0.01, frac), tunnel=frac >= 1)
    if lt > 0.5:
        top_label(frame, "NO BEAMS. NO CEMENT.", 380, YEL, 74)

def tunnel_props(frame, d, T, sc):
    lt = T - sc["s"]
    section(frame, d, T, inner_col=(70, 90, 140))
    # cold-air puffs sinking into the tunnel
    for k in range(5):
        ph = (lt * 0.6 + k / 5) % 1
        x = 800 + 110 * ph + 20 * math.sin(k)
        y = 1180 + 100 * ph
        r = 22
        d.ellipse([x - r, y - r, x + r, y + r], fill=(160, 210, 255), outline=OUTL, width=3)
    if lt > 0.5:
        top_label(frame, "COLD AIR SINKS", 380, YEL, 90)
    if lt > 1.2:
        at_label(frame, "COLD TRAP", 860, 1385, WHITE, 44)

def warm_props(frame, d, T, sc):
    lt = T - sc["s"]
    w = ease_out(clamp((lt - 0.5) / 2.0))
    col = (int(70 + 185 * w), int(90 + 110 * w), int(140 - 20 * w))
    section(frame, d, T, inner_col=col)
    if lt > 0.5:
        top_label(frame, "INSIDE: -7 TO 16 °C", 380, YEL, 80)
    if lt > 1.5:
        at_label(frame, "OUTSIDE: -45 °C", 540, 900, ICE, 56)

def kid_bed_pos(T):
    return (290, 1090, 210)

def ice_props(frame, d, T, sc):
    lt = T - sc["s"]
    section(frame, d, T, inner_col=(255, 205, 130))
    g = clamp((lt - 1.5) / 2.5)
    # glossy ice glaze growing along the inner wall
    cx, base, r = 470, 1300, 310
    rr = r - 46
    d.arc([cx - rr, base - rr * 0.95, cx + rr, base + rr * 0.95], 180, 180 + 180 * g, fill=(150, 220, 255), width=16)
    # stone lamp with flame
    lx, ly = 580, 1290
    d.chord([lx - 60, ly - 50, lx + 60, ly + 30], 0, 180, fill=(120, 110, 100), outline=OUTL, width=5)
    fl = 8 * math.sin(T * 12)
    d.polygon([(lx, ly - 60 + fl), (lx + 22, ly - 12), (lx - 22, ly - 12)], fill=(255, 190, 60), outline=OUTL)
    if lt > 0.5:
        top_label(frame, "MELT, REFREEZE, STRONGER", 380, YEL, 66)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    igloo(d, 400, 1100, 270, rows=6, tunnel=True)
    if lt > 0.5:
        top_label(frame, "GULMARG, KASHMIR", 380, YEL, 84)
    if lt > 2.0:
        at_label(frame, "11.4 M TALL", 400, 1170, WHITE, 52)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # ordinary flats with snow on top
    for i, (x, w, h) in enumerate(((150, 220, 380), (450, 240, 480), (760, 230, 340))):
        top = 1330 - h
        d.rectangle([x - w / 2, top, x + w / 2, 1330], fill=(240, 190, 140) if i % 2 else (200, 170, 230),
                    outline=OUTL, width=6)
        for yy in range(int(top) + 40, 1300, 90):
            for xx in (x - w / 4, x + w / 4):
                d.rectangle([xx - 26, yy, xx + 26, yy + 46], fill=(255, 240, 160), outline=OUTL, width=4)
        d.rounded_rectangle([x - w / 2 - 10, top - 26, x + w / 2 + 10, top + 6], radius=14, fill=SNOW, outline=OUTL,
                            width=5)
    if lt > 0.5:
        top_label(frame, "IGLU = HOUSE", 380, YEL, 100)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="cold", s=4.0, e=11.0, bg_fn=night_bg, clock="ARCTIC NIGHT", char="kid", state="puff",
         pos=(420, 1130, 380), props=cold_props, look=(0.6, -0.3),
         narr="Arctic winter nights can hit -45 °C. All you have is SNOW.", n_at=4.2, narr_y=1560,
         say="My NOSE is an ice cube!", say_at=7.2, pitch=440),
    dict(id="air", s=11.0, e=18.0, bg_fn=night_bg, clock="SECRET INGREDIENT", char="kid", pos=(320, 1130, 360),
         props=air_props, look=(0.6, 0),
         narr="Snow is up to 95% trapped AIR, so it works like a thick RAZAI.", n_at=11.2, narr_y=1560,
         say="Snow is a BLANKET?!", say_at=14.2, pitch=440),
    dict(id="build", s=18.0, e=25.0, bg_fn=day_snow_bg, clock="CONSTRUCTION", char="uncle", state="hat",
         pos=(220, 1180, 300), props=build_props, look=(0.6, 0),
         narr="Snow blocks spiral up into a curved DOME. No beams, no CEMENT.", n_at=18.2, narr_y=1560,
         say="Who needs a CONTRACTOR?", say_at=21.4, pitch=150),
    dict(id="tunnel", s=25.0, e=32.0, bg_fn=night_bg, clock="SMART DESIGN", props=tunnel_props,
         char="kid", pos=kid_bed_pos, look=(0.6, 0.2),
         narr="The door tunnel sits LOW so cold air sinks there. Your bed is RAISED.", n_at=25.2,
         narr_y=1560, say="Stay DOWN there, cold air!", say_at=28.4, pitch=440),
    dict(id="warm", s=32.0, e=39.0, bg_fn=night_bg, clock="BEDTIME", props=warm_props,
         char="kid", pos=kid_bed_pos, look=(0.4, -0.2),
         narr="Body heat alone can keep it -7 to 16 °C inside, while outside is -45.", n_at=32.2,
         narr_y=1560, say="Cosy... ISH!", say_at=35.4, pitch=440),
    dict(id="ice", s=39.0, e=46.0, bg_fn=night_bg, clock="UPGRADE", props=ice_props,
         char="uncle", state="hat", pos=(290, 1090, 210), look=(0.6, -0.3),
         narr="A lamp melts the walls a little. They refreeze into STRONGER ice.",
         n_at=39.2, narr_y=1560, say="A self-UPGRADING house!", say_at=42.4, pitch=150),
    dict(id="india", s=46.0, e=TW, bg_fn=day_snow_bg, clock="MEANWHILE IN INDIA", props=india_props,
         char="chai", pos=(820, 1150, 260), look=(-0.6, 0),
         narr="In 2022, Gulmarg opened an igloo CAFE 11.4 M tall, with 40 SEATS.", n_at=46.2,
         narr_y=1560, say="Garam chai, THANDI walls!", say_at=49.2, pitch=300),
    dict(id="twist", s=TW, e=61.0, bg="day", clock="PLOT TWIST", props=twist_props, twist=True,
         char="kid", pos=(560, 1240, 260), look=(0, -0.3),
         narr="Twist: in Inuktitut, IGLU just means HOUSE. So you already live in one.",
         n_at=TW + 0.2, narr_y=1560, say="My flat is an IGLU?!", say_at=TW + 3.4, pitch=440),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.15)
        igloo(d, 500, 1520, 230 * p, rows=5, tunnel=True)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU SLEPT IN", WHITE)], 120), 770, 0.75, "right"),
        (title([("AN IGLOO?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" sleep", WHITE)], 100), 470, 0.15),
                      (title([("in an igloo?", YEL)], 96), 600, 0.45)],
               row=[("penguin", 1), ("kid", 1), ("chai", 1), ("cloud", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, drums=False, minor=True),
           dict(t0=18.0, t1=32.0, melody=True), dict(t0=32.0, t1=46.0, drums=False, melody=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=66.0, melody=True)],
    drones=[dict(t0=4.0, dur=14.0, g=0.22)],
    fx=[("wind", 4.3, 0.35, dict(dd=6.5)), ("gale", 11.5, 0.2, dict(dd=5.0)), ("click", 19.0, 0.3),
        ("click", 19.8, 0.3), ("click", 20.6, 0.3), ("click", 21.4, 0.3), ("click", 22.2, 0.3),
        ("wind", 25.4, 0.2, dict(dd=6.0)), ("ding", 34.0, 0.25), ("bubbles", 40.5, 0.2), ("pop", 47.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_slept_in_an_igloo")
