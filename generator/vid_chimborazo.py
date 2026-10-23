#!/usr/bin/env python3
"""What if you climbed the real top of the world? Everest 8,848.86 m (Live Science). Earth bulges: equatorial radius
6,378.14 km vs polar 6,356.75 km, ~21 km (Live Science). Chimborazo, Ecuador, 6,263 m, ~1 deg S of the equator; summit
6,384.4 km from Earth's centre vs Everest 6,382.3 km, ~2.1 km farther (Wikipedia / Guinness World Records). Gravity
~9.780 m/s2 at the equator vs ~9.832 at the poles: you weigh ~0.5% less (Wikipedia, Gravity of Earth). Twist: Mauna Kea
is ~10,211 m base to peak (Live Science)."""
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

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def sky(top=(90, 160, 240), bot=(214, 236, 252)):
    y = np.linspace(0, 1, H)[:, None]
    a = (np.array(top) * (1 - y[..., None]) + np.array(bot) * y[..., None]).astype(np.uint8)
    return Image.fromarray(np.broadcast_to(a, (H, W, 3)).copy()).convert("RGBA")

def mountain(d, cx, base, h, w, col=(120, 110, 130), snow=0.32):
    peak = (cx, base - h)
    d.polygon([(cx - w, base), peak, (cx + w, base)], fill=col, outline=OUTL)
    sx = w * snow
    sy = h * snow
    d.polygon([(cx - sx, base - h + sy), peak, (cx + sx, base - h + sy), (cx + sx * 0.4, base - h + sy * 0.8),
               (cx, base - h + sy * 1.1), (cx - sx * 0.4, base - h + sy * 0.8)], fill=(250, 252, 255), outline=OUTL)

def range_bg(key, main):
    if key not in _cache:
        img = sky(); d = ImageDraw.Draw(img)
        for cx, cy, s in ((200, 560, 0.9), (860, 700, 0.7)):
            for dx, r in ((-60, 50), (0, 70), (60, 50)):
                d.ellipse([cx + (dx - r) * s, cy - r * s, cx + (dx + r) * s, cy + r * s], fill=WHITE)
        mountain(d, 120, 1350, 420, 300, (150, 140, 160))
        mountain(d, 980, 1350, 380, 280, (150, 140, 160))
        main(d)
        d.rectangle([0, 1350, W, H], fill=(110, 150, 100))
        _cache[key] = img
    return _cache[key]

def everest_bg(T):
    return range_bg("ev", lambda d: mountain(d, 540, 1350, 640, 420, (120, 110, 135)))

def chimbo_bg(T):
    def m(d):
        mountain(d, 540, 1350, 470, 400, (126, 104, 96), 0.4)
    return range_bg("ch", m)

def space_bg(T): return E.bg("space")

def ocean_bg(T):
    if "oc" not in _cache:
        img = sky((110, 180, 240), (200, 230, 250)); d = ImageDraw.Draw(img)
        _cache["oc"] = img
    return _cache["oc"]

# ---------------------------------------------------------------- props
def flag(d, x, y):
    d.line([(x, y), (x, y - 120)], fill=OUTL, width=8)
    d.polygon([(x, y - 120), (x + 90, y - 95), (x, y - 70)], fill=(230, 50, 60), outline=OUTL)

def everest_props(frame, d, T, sc):
    lt = T - sc["s"]
    flag(d, 610, 720)
    if lt > 0.6:
        top_label(frame, "8,849 M", 380, YEL, 90)

def bulge_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 1.0) / 2.5))
    spr = draw_char("earth", 520, T, 0, False, (0, 0), T * 0.6)
    w, h = int(520 * (1 + 0.16 * p)), int(520 * (1 - 0.08 * p))
    spr = spr.resize((w, h), Image.BILINEAR)
    comp(frame, spr, 540 - w / 2, 960 - h / 2)
    # the "perfect ball" outline for comparison
    r = 210
    d.ellipse([540 - r, 960 - r, 540 + r, 960 + r], outline=WHITE, width=4)
    if lt > 3.5:
        lab_at(frame, "(SHAPE EXAGGERATED)", 540, 1290, WHITE, 40)

def radius_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, rx, ry = 540, 960, 400, 340
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(60, 130, 220), outline=OUTL, width=8)
    for bx, by, bw, bh in ((-230, -120, 160, 110), (60, -200, 200, 140), (-90, 80, 180, 140), (170, 70, 140, 100)):
        d.ellipse([cx + bx, cy + by, cx + bx + bw, cy + by + bh], fill=(90, 180, 100))
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 90, 60), outline=OUTL, width=4)
    if lt > 0.8:
        q = ease_out(clamp((lt - 0.8) / 0.6))
        d.line([(cx, cy), (cx + rx * q, cy)], fill=YEL, width=12)
    if lt > 1.8:
        q = ease_out(clamp((lt - 1.8) / 0.6))
        d.line([(cx, cy), (cx, cy - ry * q)], fill=WHITE, width=12)
    if lt > 1.4:
        lab_at(frame, "6,378 KM", cx + 200, cy + 60, YEL, 54)
    if lt > 2.4:
        lab_at(frame, "6,357 KM", cx + 130, cy - 200, WHITE, 54)
    if lt > 3.0:
        top_label(frame, "+21 KM AT THE EQUATOR", 380, YEL, 64)

def chimbo_props(frame, d, T, sc):
    lt = T - sc["s"]
    flag(d, 600, 900)
    if lt > 0.6:
        top_label(frame, "6,263 M", 380, YEL, 90)
    if lt > 1.2:
        lab_at(frame, "ECUADOR", 860, 1120, WHITE, 50)

def far_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, rx, ry = 380, 1040, 300, 270
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(60, 130, 220), outline=OUTL, width=8)
    d.line([(cx - rx, cy), (cx + rx, cy)], fill=(255, 255, 255), width=3)
    # Everest at ~28 deg N, Chimborazo at the equator (heights hugely exaggerated)
    a = math.radians(28)
    ex, ey = cx + rx * math.cos(a), cy - ry * math.sin(a)
    d.polygon([(ex - 30, ey + 14), (ex + 40, ey - 60), (ex + 50, ey + 20)], fill=(150, 140, 160), outline=OUTL)
    px, py = cx + rx, cy
    d.polygon([(px - 10, py - 40), (px + 70, py), (px - 10, py + 40)], fill=(126, 104, 96), outline=OUTL)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 90, 60), outline=OUTL, width=4)
    if lt > 0.6:
        q = ease_out(clamp((lt - 0.6) / 0.6))
        d.line([(cx, cy), (cx + (ex + 40 - cx) * q, cy + (ey - 60 - cy) * q)], fill=WHITE, width=10)
    if lt > 1.6:
        q = ease_out(clamp((lt - 1.6) / 0.6))
        d.line([(cx, cy), (cx + (px + 70 - cx) * q, cy)], fill=YEL, width=10)
    if lt > 1.2:
        lab_at(frame, "EVEREST", 800, 760, WHITE, 52)
        lab_at(frame, "6,382 KM", 800, 825, WHITE, 52)
    if lt > 2.2:
        lab_at(frame, "CHIMBORAZO", 800, 1150, YEL, 52)
        lab_at(frame, "6,384 KM", 800, 1215, YEL, 52)
    if lt > 3.0:
        top_label(frame, "FARTHEST FROM THE CENTRE", 380, YEL, 58)

def scale_props(frame, d, T, sc):
    lt = T - sc["s"]
    x, y = 540, 1230
    d.rounded_rectangle([x - 200, y - 50, x + 200, y + 40], radius=20, fill=(230, 232, 240), outline=OUTL, width=6)
    d.rounded_rectangle([x - 90, y - 30, x + 90, y + 20], radius=8, fill=(40, 50, 60))
    v = 60.0 - 0.3 * clamp((lt - 1.5) / 2.0)
    l = label(f"{v:.1f} KG", 40, (120, 255, 140)); comp(frame, l, x - l.width / 2, y - 40)
    if lt > 1.0:
        lab_at(frame, "POLE", 220, 600, WHITE, 52) if lt < 1.5 else lab_at(frame, "EQUATOR", 220, 600, YEL, 52)
    if lt > 3.6:
        top_label(frame, "-0.5%", 380, YEL, 90)

def mauna_props(frame, d, T, sc):
    lt = T - sc["s"]
    sea = 1168
    p = ease_out(clamp(lt / 1.2))
    mountain(d, 540, 1900, 1180 * p + 60, 560, (96, 80, 72), 0.08)
    # translucent water over the underwater part
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    ld.rectangle([0, sea, W, H], fill=(30, 110, 190, 150))
    frame.alpha_composite(layer)
    d2 = ImageDraw.Draw(frame)
    for x in range(0, W, 120):
        d2.arc([x, sea - 20, x + 120, sea + 20], 0, 180, fill=WHITE, width=5)
    if lt > 2.0:
        d2.line([(800, 1880), (800, 1900 - 1240)], fill=YEL, width=8)
        d2.line([(770, 1900 - 1240), (830, 1900 - 1240)], fill=YEL, width=8)
        lab_at(frame, "~10,200 M", 760, 1900 - 1300, YEL, 54)
        lab_at(frame, "SEA LEVEL", 220, sea - 50, WHITE, 44)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="everest", s=4.0, e=11.0, bg_fn=everest_bg, clock="MOUNT EVEREST", char="kid",
         pos=(540, 800, 260), props=everest_props, look=(0, -0.2),
         narr="Everest stands 8,849 METRES above sea level. The HIGHEST point on Earth.", n_at=4.2,
         say="TOP of the world!", say_at=7.6, pitch=400, bubble_y=560),
    dict(id="bulge", s=11.0, e=18.0, bg_fn=space_bg, clock="PROBLEM", props=bulge_props,
         narr="But Earth isn't a perfect ball. Its spin makes it BULGE at the equator.", n_at=11.2),
    dict(id="radius", s=18.0, e=25.0, bg_fn=space_bg, clock="THE BULGE", props=radius_props,
         narr="The equator sits about 21 KM farther from Earth's centre than the poles.", n_at=18.2),
    dict(id="chimbo", s=25.0, e=32.0, bg_fn=chimbo_bg, clock="CHIMBORAZO", char="uncle", state="hat",
         pos=(540, 960, 240), props=chimbo_props, look=(0, 0.2),
         narr="Chimborazo in Ecuador sits right near the equator. Only 6,263 METRES tall.", n_at=25.2,
         say="Chhota sa PAHAD?", say_at=28.6, pitch=150, bubble_y=680),
    dict(id="far", s=32.0, e=39.0, bg_fn=space_bg, clock="FROM THE CENTRE", props=far_props,
         narr="But its peak is about 2 KM FARTHER from Earth's centre than Everest's!", n_at=32.2),
    dict(id="scale", s=39.0, e=46.0, bg="pole", clock="BONUS", char="uncle", pos=(540, 1000, 400),
         props=scale_props, look=(0, 0.5),
         narr="Bonus: you'd weigh about 0.5% LESS at the equator than at the poles.", n_at=39.2,
         say="Free WEIGHT LOSS!", say_at=42.8, pitch=150),
    dict(id="twist", s=46.0, e=53.0, bg_fn=ocean_bg, clock="PLOT TWIST", twist=True, props=mauna_props,
         narr="Twist: from its base on the sea floor, Hawaii's Mauna Kea is about 10,200 METRES tall!",
         n_at=46.2, narr_y=1500),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back(clamp((T - 1.9) / 0.5))
        mountain(d, 540, 1560, 260 * p + 1, 220, (120, 110, 135))

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU CLIMBED THE", WHITE)], 120), 770, 0.75, "right"),
        (title([("REAL ", WHITE), ("TOP OF THE WORLD?", YEL)], 110), 910, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which is the ", WHITE), ("REAL", YEL)], 100), 470, 0.15),
                      (title([("top of the world?", YEL)], 104), 600, 0.45)],
               row=[("kid", 1), ("uncle", "hat"), ("earth", 1), ("uncle", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=45.85), dict(t0=53.0, t1=58.0, melody=True)],
    drones=[dict(t0=46.2, dur=6.6, g=0.3)],
    fx=[("wind", 4.2, 0.3, dict(dd=6.0)), ("wind", 25.2, 0.3, dict(dd=6.0)), ("pop", 19.0, 0.4),
        ("pop", 20.0, 0.4), ("ding", 35.0, 0.3), ("waves", 46.3, 0.4, dict(dd=6.0)), ("ding", 50.2, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_climbed_the_real_top_of_the_world")
