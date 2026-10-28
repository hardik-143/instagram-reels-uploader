#!/usr/bin/env python3
"""What if you swam in Lake Natron? Northern Tanzania, near Ol Doinyo Lengai; shallow (< 3 m); red/orange colour from
salt-loving cyanobacteria with red pigment; often above 40 °C, up to 60 °C; pH 9-10.5, can exceed 12 (Wikipedia: Lake
Natron; Smithsonian). Caustic enough to burn the skin and eyes of unadapted animals (Smithsonian). Natron salt was
used in ancient Egyptian mummification as a drying agent (Wikipedia: Natron). ~2.5 million lesser flamingos; 75% of
the world's lesser flamingos are born here; they nest on salt islands protected by a caustic moat (Wikipedia,
Smithsonian). Calcified animals: Nick Brandt 'took these creatures as I found them on the shoreline, and then placed
them in living positions' (PetaPixel); the lake's minerals preserve bodies of animals that already died.
India: lesser flamingos also breed in Gujarat's Little Rann of Kutch (Wikipedia: Lesser flamingo); flocks that winter
in Mumbai arrive around November and come mostly from Gujarat (Smithsonian, 2023)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 56.0   # twist start
PINK = (250, 150, 170)
PINK_D = (230, 110, 140)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=56, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def lake_bg(kind="red"):
    if kind in _bgc: return _bgc[kind]
    sky = {"red": [(0, (255, 170, 110)), (0.55, (255, 214, 160)), (1, (255, 214, 160))],
           "mumbai": [(0, (120, 180, 240)), (0.55, (210, 232, 250)), (1, (210, 232, 250))]}[kind]
    img = grad(sky, W, H); d = ImageDraw.Draw(img)
    if kind == "red":
        d.polygon([(380, 1000), (640, 640), (720, 640), (1000, 1000)], fill=(150, 100, 90))   # Ol Doinyo Lengai
        d.polygon([(600, 690), (640, 640), (720, 640), (760, 690), (700, 670), (660, 690)], fill=(240, 236, 230))
        d.polygon([(0, 1000), (200, 880), (420, 1000)], fill=(170, 120, 100))
        d.rectangle([0, 1000, W, H], fill=(205, 60, 50))
        for k in range(14):
            y = 1040 + k * 62
            for j in range(4):
                x = (k * 173 + j * 290) % 1180 - 60
                d.rounded_rectangle([x, y, x + 120 + (k % 3) * 40, y + 10], 5, fill=(230, 100, 70))
        for x, y, w_ in ((80, 1130, 220), (760, 1210, 260), (420, 1620, 300)):
            d.ellipse([x, y, x + w_, y + 50], fill=(245, 225, 215))
    else:
        for k, (x, h) in enumerate(((60, 300), (180, 420), (320, 360), (760, 460), (900, 330))):
            d.rectangle([x, 1000 - h, x + 110, 1000], fill=(150, 160, 190))
            for r in range(int(h / 60)):
                d.rectangle([x + 20, 1000 - h + 20 + r * 60, x + 45, 1000 - h + 45 + r * 60], fill=(230, 235, 250))
                d.rectangle([x + 65, 1000 - h + 20 + r * 60, x + 90, 1000 - h + 45 + r * 60], fill=(230, 235, 250))
        d.rectangle([0, 1000, W, H], fill=(150, 130, 110))
        for k in range(10):
            y = 1040 + k * 80
            d.rounded_rectangle([(k * 210) % 900, y, (k * 210) % 900 + 200, y + 12], 6, fill=(170, 200, 220))
    img = img.convert("RGBA")
    _bgc[kind] = img
    return img

# ---------------------------------------------------------------- flamingo
def flamingo(d, x, y, s, T, phase=0.0, stone=False, flip=False):
    """Flamingo standing on one leg; (x, y) = foot position on the ground."""
    body = (200, 196, 190) if stone else PINK
    dark = (160, 155, 150) if stone else PINK_D
    beak = (120, 115, 110) if stone else (40, 30, 30)
    f = -1 if flip else 1
    bob = 0 if stone else 4 * s * math.sin(T * 2.4 + phase)
    X = lambda dx: x + f * dx * s
    by = y - 260 * s + bob
    # leg
    d.line([(x, y), (x, by + 30 * s)], fill=OUTL, width=max(3, int(10 * s)))
    d.line([(x, y), (x, by + 30 * s)], fill=dark, width=max(2, int(6 * s)))
    d.line([(x, by + 110 * s), (X(40), by + 80 * s), (x, by + 60 * s)], fill=dark, width=max(2, int(6 * s)))
    # body
    d.ellipse([X(-90) if f > 0 else X(90), by - 60 * s, X(90) if f > 0 else X(-90), by + 50 * s],
              fill=body, outline=OUTL, width=max(2, int(5 * s)))
    d.polygon([(X(-80), by - 20 * s), (X(-140), by - 30 * s), (X(-90), by + 20 * s)], fill=dark, outline=OUTL)
    d.ellipse([X(-50) if f > 0 else X(50), by - 40 * s, X(40) if f > 0 else X(-40), by + 20 * s], fill=dark)
    # S-neck
    pts = [(X(60), by - 30 * s), (X(100), by - 90 * s), (X(60), by - 150 * s), (X(30), by - 200 * s),
           (X(60), by - 250 * s)]
    d.line(pts, fill=OUTL, width=max(4, int(26 * s)), joint="curve")
    d.line(pts, fill=body, width=max(3, int(18 * s)), joint="curve")
    hx, hy = X(75), by - 260 * s
    d.ellipse([hx - 28 * s, hy - 24 * s, hx + 28 * s, hy + 24 * s], fill=body, outline=OUTL, width=max(2, int(4 * s)))
    d.polygon([(X(95), hy - 10 * s), (X(150), hy + 10 * s), (X(130), hy + 45 * s), (X(98), hy + 18 * s)],
              fill=(250, 245, 240) if not stone else body, outline=OUTL)
    d.polygon([(X(130), hy + 10 * s), (X(150), hy + 10 * s), (X(130), hy + 45 * s)], fill=beak)
    if stone:
        d.line([(hx - 8 * s, hy - 2 * s), (hx + 8 * s, hy + 6 * s)], fill=OUTL, width=max(2, int(4 * s)))
    else:
        d.ellipse([hx - 4 * s + f * 6 * s, hy - 10 * s, hx + 8 * s + f * 6 * s, hy + 2 * s], fill=OUTL)

def flock(d, T, n=9, y0=1080, s=0.42):
    for k in range(n):
        x = 90 + (k * 137) % 920
        y = y0 + (k % 3) * 90
        flamingo(d, x, y, s * (0.85 + 0.15 * (k % 3)), T, k * 0.7, flip=(k % 2 == 1))

# ---------------------------------------------------------------- scene props
def microbes(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(9):
        x = 160 + (k * 191) % 800; y = 1060 + (k * 97) % 250 + 12 * math.sin(lt * 2 + k)
        r = 34 + (k % 3) * 10
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(170, 30, 40), outline=OUTL, width=4)
        d.ellipse([x - r * 0.4, y - r * 0.25, x - r * 0.1, y + r * 0.05], fill=(240, 120, 110))
    if lt > 1.5: put_label(frame, "MICROBES, NOT BLOOD", 540, 760, 54)

def ph_props(frame, d, T, sc):
    lt = T - sc["s"]
    x0, x1, y = 120, 960, 820
    cols = [(230, 60, 50), (240, 140, 50), (250, 220, 60), (120, 200, 80), (60, 160, 200), (70, 90, 200),
            (110, 60, 170)]
    for i, c in enumerate(cols):
        a = x0 + (x1 - x0) * i / 7; b = x0 + (x1 - x0) * (i + 1) / 7
        d.rectangle([a, y, b, y + 70], fill=c)
    d.rectangle([x0, y, x1, y + 70], outline=OUTL, width=5)
    for v, txt, col in ((7, "POOL 7", WHITE), (10.5, "NATRON 10+", YEL)):
        px = x0 + (x1 - x0) * v / 14
        if txt.startswith("NATRON") and lt < 1.8: continue
        if txt.startswith("POOL"): d.polygon([(px - 24, y - 50), (px + 24, y - 50), (px, y - 6)], fill=col, outline=OUTL)
        if txt.startswith("POOL"):
            put_label(frame, txt, px, y - 140, 52, col)
        else:
            d.polygon([(px - 24, y + 120), (px + 24, y + 120), (px, y + 76)], fill=col, outline=OUTL)
            put_label(frame, txt, px, y + 110, 52, col)
    if lt > 3.0: put_label(frame, "BURNS SKIN + EYES", 540, 1080, 60, WHITE)

def heat_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(3):
        yy = 560 + k * 60
        pts = [(220 + i * 40, yy + 12 * math.sin(lt * 6 + i + k)) for i in range(17)]
        d.line(pts, fill=(255, 245, 220), width=6)
    for k in range(4):
        ph = (lt * 0.8 + k / 4) % 1.0
        x = 540 + (k - 1.5) * 170; y = 820 + ph * 120
        d.ellipse([x - 12, y - 18, x + 12, y + 18], fill=(150, 210, 255), outline=OUTL, width=3)

def mummy(d, cx, cy, s=1.0):
    d.rounded_rectangle([cx - 90 * s, cy - 260 * s, cx + 90 * s, cy + 220 * s], int(80 * s), fill=(235, 225, 200),
                        outline=OUTL, width=6)
    for k in range(9):
        y = cy - 200 * s + k * 48 * s
        d.line([(cx - 85 * s, y), (cx + 85 * s, y + 20 * s)], fill=(200, 188, 160), width=6)
    for ex in (-30, 30):
        d.ellipse([cx + (ex - 14) * s, cy - 175 * s, cx + (ex + 14) * s, cy - 147 * s], fill=OUTL)

def salt_props(frame, d, T, sc):
    lt = T - sc["s"]
    mummy(d, 700, 1050, 0.9)
    d.polygon([(120, 1250), (330, 1060), (540, 1250)], fill=(250, 250, 255), outline=OUTL)
    for k in range(6):
        x = 170 + k * 60; y = 1240 - (k % 2) * 40
        d.polygon([(x, y), (x + 30, y - 50), (x + 60, y)], fill=(235, 240, 250), outline=OUTL)
    if lt > 1.5: put_label(frame, "NATRON", 330, 940, 64, YEL)

def flock_props(frame, d, T, sc):
    lt = T - sc["s"]
    flock(d, T, 9, 1080, 0.5)
    if lt > 2.0: put_label(frame, "2.5 MILLION", 540, 780, 80)

def island_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.ellipse([260, 1040, 820, 1200], fill=(245, 230, 220), outline=OUTL, width=5)
    for k in range(5):
        x = 330 + k * 105; y = 1110 + (k % 2) * 20
        d.polygon([(x - 34, y), (x + 34, y), (x + 22, y - 36), (x - 22, y - 36)], fill=(170, 140, 120), outline=OUTL)
        d.ellipse([x - 16, y - 54, x + 16, y - 26], fill=(250, 250, 245), outline=OUTL, width=3)
    flamingo(d, 470, 1080, 0.5, T, 0.0); flamingo(d, 640, 1090, 0.5, T, 1.0, flip=True)
    # a hyena-ish predator stuck at the shore
    hx = 900 + 10 * math.sin(lt * 3)
    d.ellipse([hx - 70, 1110, hx + 70, 1180], fill=(170, 140, 100), outline=OUTL, width=4)
    d.ellipse([hx - 110, 1090, hx - 40, 1150], fill=(170, 140, 100), outline=OUTL, width=4)
    if lt > 2.2: put_label(frame, "SAFE NURSERY", 540, 780, 64)

def stone_props(frame, d, T, sc):
    lt = T - sc["s"]
    flamingo(d, 560, 1270, 0.95, T, 0, stone=True)
    if lt > 1.0:
        put_label(frame, "TURNED TO STONE?", 540, 680, 64, WHITE)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 1.0) / 0.8))
    flamingo(d, 720, 1290, 0.85, T, 0, stone=True)
    # a hand placing it
    hx = 720 + 140 - 40 * p; hy = 700 + 140 * p
    d.rounded_rectangle([hx, hy, hx + 90, hy + 70], 30, fill=(226, 168, 118), outline=OUTL, width=5)
    d.rectangle([hx + 70, hy - 160, hx + 120, hy + 30], fill=(80, 90, 130), outline=OUTL, width=5)
    if lt > 3.2: put_label(frame, "POSED!", 300, 760, 90)

def mumbai_props(frame, d, T, sc):
    lt = T - sc["s"]
    flock(d, T, 9, 1080, 0.40)
    if lt > 2.2: put_label(frame, "MUMBAI, EVERY WINTER", 540, 760, 60)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="arrive", s=4.0, e=10.5, bg_fn=lambda T: lake_bg(), clock="TANZANIA", char="kid", pos=(540, 1080, 420),
         look=(0, 0.4),
         narr="Northern TANZANIA. A shallow lake that looks BLOOD red.", n_at=4.2,
         say="Is that... JUICE?", say_at=6.8, pitch=620),
    dict(id="red", s=10.5, e=17.0, bg_fn=lambda T: lake_bg(), clock="WHY RED?", props=microbes,
         narr="The red? Salt-loving MICROBES with a red pigment. Not blood. Phew.", n_at=10.7),
    dict(id="ph", s=17.0, e=23.5, bg_fn=lambda T: lake_bg(), clock="pH TEST", props=ph_props,
         narr="Pool water: pH 7. Natron: pH 10 and higher, strong enough to BURN skin.", n_at=17.2),
    dict(id="heat", s=23.5, e=30.0, bg_fn=lambda T: lake_bg(), clock="40-60 °C", char="kid", state="puff",
         pos=(540, 1080, 420), props=heat_props, look=(0, -0.3),
         narr="And HOT: often above 40 °C, up to 60 °C in spots.", n_at=23.7,
         say="Hot TUB? No thanks!", say_at=26.3, pitch=620),
    dict(id="salt", s=30.0, e=36.5, bg="digsite", clock="THE SALT", props=salt_props,
         narr="Its salt, NATRON, is what ancient Egyptians used to dry out MUMMIES.", n_at=30.2),
    dict(id="flock", s=36.5, e=43.0, bg_fn=lambda T: lake_bg(), clock="SURPRISE", props=flock_props,
         narr="Yet about 2.5 MILLION flamingos live here. 75% of all lesser flamingos are BORN here.",
         n_at=36.7),
    dict(id="nursery", s=43.0, e=49.5, bg_fn=lambda T: lake_bg(), clock="WHY HERE?", props=island_props,
         narr="They nest on salt ISLANDS. The caustic water keeps PREDATORS away.", n_at=43.2),
    dict(id="stone", s=49.5, e=TW, bg_fn=lambda T: lake_bg(), clock="VIRAL PHOTOS", props=stone_props,
         narr="But those viral photos of birds turned to STONE in seconds?", n_at=49.7),
    dict(id="twist", s=TW, e=63.0, bg_fn=lambda T: lake_bg(), clock="PLOT TWIST", char="uncle", state="hat",
         pos=(300, 1060, 300), props=twist_props, twist=True, look=(0.5, 0.2),
         narr="Twist: the photographer POSED them. The lake slowly preserves birds that already DIED.",
         n_at=TW + 0.2),
    dict(id="mumbai", s=63.0, e=69.5, bg_fn=lambda T: lake_bg("mumbai"), clock="INDIA", props=mumbai_props,
         narr="Lesser flamingos live in INDIA too. Every winter they turn MUMBAI pink!", n_at=63.2),
    dict(id="outro", s=69.5, e=74.5),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.45)
        flamingo(d, 540, 1720, 0.8 * max(0.05, p), T, 0)

cfg = dict(
    total=74.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("you ", WHITE), ("SWAM", YEL), (" in", WHITE)], 120), 770, 0.75, "right"),
        (title([("the RED", WHITE)], 110), 905, 1.05, "left"),
        (title([("LAKE NATRON?", YEL)], 130), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would", WHITE), (" YOU", YEL), (" visit", WHITE)], 96), 470, 0.15),
                      (title([("Lake Natron?", YEL)], 100), 600, 0.45)],
               row=[("kid", 1), ("uncle", "hat"), ("sun", 1), ("fish", 1), ("earth", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=69.5, t1=74.5, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.06)],
    fx=[("bubbles", 10.8, 0.4, dict(dd=5.0)), ("wind", 23.7, 0.3, dict(dd=5.0)), ("seagulls", 36.8, 0.5),
        ("seagulls", 63.3, 0.5), ("click", TW + 1.4, 0.8)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_lake_natron")
