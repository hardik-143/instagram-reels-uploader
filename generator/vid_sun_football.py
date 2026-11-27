#!/usr/bin/env python3
"""What if the Sun were a football? Scale model with the Sun = a 22 cm football (FIFA size 5, 68-70 cm round).
Scale from NASA diameters/distances: Sun 1,392,700 km; Earth 12,742 km -> 2.0 mm (mustard seed) at 1 AU -> 23.6 m
(a cricket pitch is 20.12 m, 22 yards); Moon 3,475 km -> 0.55 mm at 384,400 km -> 6 cm; ISS ~400 km up -> 0.06 mm
(about a hair's width); Jupiter 139,820 km -> 2.2 cm at 5.2 AU -> 123 m; Neptune 49,244 km -> 7.8 mm at 30.07 AU -> 710 m.
News: Voyager 1 reached one light-day (25.9 billion km) from Earth at 5:16 a.m. EST on 18 Nov 2026, 49 years after its
5 Sep 1977 launch (NASA release 19 Nov 2026; NASA Science 'What is a light-day') -> 4.1 km on this model.
Twist: Proxima Centauri, the nearest star, 4.25 light-years -> about 6,300 km (Delhi-London great circle ~6,700 km)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 60.0

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

def char_at(frame, kind, cx, cy, B, T, state=1, look=(0, 0.15)):
    if B < 6: return
    spr = draw_char(kind, int(B), T, 0.0, False, look, state)
    comp(frame, spr, cx - spr.width / 2, cy - spr.height / 2)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def field_bg(T):
    """Green cricket ground with a brown pitch strip running left to right."""
    if "field" not in _cache:
        img = E.grad([(0, (120, 190, 250)), (0.35, (200, 232, 252)), (0.36, (90, 170, 90)), (1, (70, 150, 74))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        for k in range(8):
            y0 = 700 + k * 150
            d.rectangle([0, y0, W, y0 + 75], fill=(80, 160, 82))
        d.rectangle([0, 1080, W, 1260], fill=(214, 186, 130), outline=OUTL, width=5)
        _cache["field"] = img
    return _cache["field"].copy()

def stumps(d, x, y=1130):
    for k in (-14, 0, 14):
        d.rectangle([x + k - 4, y - 90, x + k + 4, y], fill=(250, 240, 210), outline=OUTL, width=2)
    d.line([(x - 20, y - 92), (x + 20, y - 92)], fill=(200, 150, 80), width=5)

def football(frame, cx, cy, B, T):
    char_at(frame, "football", cx, cy, B, T)

def jupiter(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(222, 170, 120), outline=OUTL, width=max(2, int(r * 0.12)))
    for k, col in ((-0.45, (180, 120, 80)), (0.0, (240, 210, 170)), (0.4, (180, 120, 80))):
        y = cy + k * r; hw = r * math.sqrt(max(0.0, 1 - k * k)) * 0.92
        d.line([(cx - hw, y), (cx + hw, y)], fill=col, width=max(2, int(r * 0.18)))

def neptune(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(80, 130, 240), outline=OUTL, width=max(2, int(r * 0.14)))

def probe(d, cx, cy, s=1.0):
    d.ellipse([cx - 70 * s, cy - 110 * s, cx + 70 * s, cy - 50 * s], fill=WHITE, outline=OUTL, width=5)
    d.rectangle([cx - 45 * s, cy - 50 * s, cx + 45 * s, cy + 20 * s], fill=(220, 200, 140), outline=OUTL, width=5)
    d.line([(cx + 45 * s, cy), (cx + 200 * s, cy + 40 * s)], fill=OUTL, width=5)
    d.line([(cx - 45 * s, cy), (cx - 160 * s, cy + 70 * s)], fill=OUTL, width=5)
    d.ellipse([cx + 190 * s, cy + 30 * s, cx + 214 * s, cy + 54 * s], fill=(200, 200, 210), outline=OUTL, width=3)

def magnifier(frame, cx, cy, r, inner_fn):
    """Draw a lens with a magnified scene inside (inner_fn(layer, draw, cx, cy, r))."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 26, 50))
    inner_fn(L, ld, cx, cy, r)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    frame.paste(L, (0, 0), Image.composite(L, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask).split()[3])
    d = ImageDraw.Draw(frame)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=OUTL, width=16)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], outline=(200, 200, 210), width=6)
    a = math.radians(45)
    x0, y0 = cx + math.cos(a) * r, cy + math.sin(a) * r
    d.line([(x0, y0), (x0 + 120, y0 + 120)], fill=(120, 80, 50), width=34)

# ---------------------------------------------------------------- props
def shrink_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.4) / 2.2))
    if lt < 2.8:
        char_at(frame, "sun", 540, 1020, 560 - 360 * p, T)
    else:
        q = min(ease_back(clamp((lt - 2.8) / 0.5)), 1.1)
        football(frame, 540, 1020, 320 * q, T)
    if lt > 0.4: top_label(frame, "SUN = A FOOTBALL", 380, YEL, 96)
    if lt > 3.2: at_label(frame, "22 CM WIDE", 540, 820, WHITE, 64)

def seed_props(frame, d, T, sc):
    lt = T - sc["s"]
    football(frame, 200, 1160, 200, T)
    d.ellipse([538, 1176, 546, 1184], fill=(60, 120, 200), outline=OUTL, width=1)
    if lt > 0.8:
        g = min(ease_back(clamp((lt - 0.8) / 0.6)), 1.08)
        def inner(L, ld, cx, cy, r):
            spr = draw_char("earth", int(260 * g) + 4, T, 0.0, False, (0, 0.1), T * 0.2)
            L.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))
        magnifier(frame, 680, 960, 220, inner)
    if lt > 0.4: top_label(frame, "EARTH = MUSTARD SEED", 380, YEL, 80)
    if lt > 2.0: at_label(frame, "ABOUT 2 MM", 680, 680, WHITE, 60)

PX0, PX1 = 120, 870          # football end and far stumps: 20.12 m
def mx(m): return PX0 + (PX1 - PX0) * m / 20.12

def pitch_props(frame, d, T, sc):
    lt = T - sc["s"]
    stumps(d, PX0 + 40); stumps(d, PX1)
    football(frame, PX0, 1170, 170, T)
    g = ease_out(clamp((lt - 0.6) / 3.0))
    m = 23.6 * g
    x = mx(m)
    if lt > 0.6:
        d.line([(PX0 + 80, 1240), (x, 1240)], fill=YEL, width=8)
        d.ellipse([x - 7, 1173, x + 7, 1187], fill=(60, 120, 200), outline=OUTL, width=2)
        at_label(frame, f"{m:.1f} M", min(x, 880), 1300, WHITE, 56)
    if lt > 3.8: at_label(frame, "PITCH: 20 M", (PX0 + PX1) / 2, 980, WHITE, 52)
    if lt > 0.4: top_label(frame, "EARTH IS HERE", 380, YEL, 96)

def moon_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = min(ease_back(clamp((lt - 0.3) / 0.6)), 1.08)
    def inner(L, ld, cx, cy, r):
        spr = draw_char("earth", int(190 * g) + 4, T, 0.0, False, (0.5, 0), T * 0.2)
        L.alpha_composite(spr, (int(cx - 160 - spr.width / 2), int(cy - spr.height / 2)))
        if lt > 1.0:
            ms = draw_char("moon", 70, T, 0.0, False, (-0.5, 0))
            L.alpha_composite(ms, (int(cx + 190 - 35), int(cy - 35)))
            ld.line([(cx - 60, cy + 110), (cx + 190, cy + 110)], fill=YEL, width=6)
        if lt > 3.3:  # ISS orbit: a hairline hugging Earth
            ld.ellipse([cx - 160 - 92, cy - 92, cx - 160 + 92, cy + 92], outline=(255, 120, 120), width=3)
    magnifier(frame, 540, 1000, 330, inner)
    if lt > 1.4: at_label(frame, "6 CM", 600, 1160, YEL, 52)
    if lt > 3.5: at_label(frame, "ISS: 0.06 MM UP", 540, 600, (255, 160, 160), 60)
    if lt > 0.4: top_label(frame, "MOON = A SAND GRAIN", 380, YEL, 80)

def jup_props(frame, d, T, sc):
    lt = T - sc["s"]
    football(frame, 130, 1170, 130, T)
    d.line([(520, 700), (520, 1330)], fill=WHITE, width=8)
    if lt > 0.6: at_label(frame, "BOUNDARY", 520, 660, WHITE, 46)
    g = ease_out(clamp((lt - 1.0) / 2.0))
    x = 200 + (820 - 200) * g
    jupiter(d, x, 1170, 30)
    if lt > 3.0:
        at_label(frame, "123 M", 800, 1270, YEL, 60)
        at_label(frame, "2 CM MARBLE", 780, 1080, WHITE, 50)
    if lt > 0.4: top_label(frame, "JUPITER", 380, YEL, 110)

def nep_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.5) / 4.5))
    neptune(d, 800, 1180, 14)
    at_label(frame, "8 MM BEAD", 790, 1100, WHITE, 50)
    if lt > 0.4: top_label(frame, f"NEPTUNE: {int(710 * g)} M", 380, YEL, 90)

def voy_props(frame, d, T, sc):
    lt = T - sc["s"]
    x = 420 + 60 * math.sin(T * 0.8)
    probe(d, x, 1000, 1.9)
    if lt > 0.4: top_label(frame, "1 LIGHT-DAY AWAY", 380, YEL, 86)
    if lt > 3.0: at_label(frame, "ON OUR MODEL: 4 KM", 600, 1250, WHITE, 60)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    ax, ay, bx, by = 260, 1150, 820, 820
    g = ease_out(clamp((lt - 0.8) / 2.0))
    pts = []
    for k in range(41):
        t = k / 40 * g
        x = ax + (bx - ax) * t; y = ay + (by - ay) * t - 160 * math.sin(math.pi * t)
        pts.append((x, y))
    for k in range(0, len(pts) - 1, 2):
        d.line([pts[k], pts[k + 1]], fill=YEL, width=8)
    for (x, y, n) in ((ax, ay, "DELHI"), (bx, by, "LONDON")):
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(240, 80, 70), outline=OUTL, width=4)
        at_label(frame, n, x, y + 60, WHITE, 52)
    if lt > 2.8:
        char_at(frame, "sun", bx + 20, by - 170, 150 * min(ease_back(clamp((lt - 2.8) / 0.4)), 1.1), T)
    if lt > 0.4: top_label(frame, "NEAREST STAR: 6,300 KM", 380, YEL, 76)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="shrink", s=4.0, e=11.0, bg="space", clock="SHRINK RAY", props=shrink_props,
         narr="Shrink the SUN to the size of a FOOTBALL. Now scale EVERYTHING the same.",
         n_at=4.2, narr_y=1560),
    dict(id="seed", s=11.0, e=18.0, bg_fn=field_bg, clock="SCALE MODEL", props=seed_props,
         narr="EARTH becomes a MUSTARD SEED, about 2 MM wide.", n_at=11.2, narr_y=1560),
    dict(id="pitch", s=18.0, e=25.0, bg_fn=field_bg, clock="ON THE PITCH", props=pitch_props,
         narr="And it sits about 24 METRES away, past the far end of a CRICKET PITCH.",
         n_at=18.2, narr_y=1560),
    dict(id="moon", s=25.0, e=32.0, bg="space", clock="ZOOM IN", props=moon_props,
         narr="The MOON: a speck 6 CM from the seed. The ISS flies just a HAIR'S WIDTH up.",
         n_at=25.2, narr_y=1560),
    dict(id="jup", s=32.0, e=39.0, bg_fn=field_bg, clock="KEEP WALKING", props=jup_props,
         narr="JUPITER: a 2 CM marble, about 123 METRES out. Past the BOUNDARY!",
         n_at=32.2, narr_y=1560),
    dict(id="nep", s=39.0, e=46.0, bg="space", clock="9-MIN WALK", props=nep_props,
         char="kid", pos=(330, 1130, 360), look=(0.6, 0.1),
         narr="NEPTUNE: an 8 MM bead, 710 METRES away. Nearly empty space all the way.",
         n_at=39.2, narr_y=1560, say="Are we THERE yet?", say_at=42.2, pitch=440),
    dict(id="voy", s=46.0, e=53.0, bg="space", clock="NEWS: 18 NOV", props=voy_props,
         narr="On 18 NOV, VOYAGER 1 hit ONE LIGHT-DAY from Earth after 49 YEARS of flying.",
         n_at=46.2, narr_y=1560),
    dict(id="hint", s=53.0, e=TW, bg_fn=field_bg, clock="QUIZ TIME", char="kid", pos=(540, 1060, 420),
         narr="So on this model, how far is the NEAREST STAR? Next street? Next city?",
         n_at=53.2, narr_y=1560, say="Next DOOR, surely!", say_at=56.0, pitch=440),
    dict(id="twist", s=TW, e=67.5, bg="space", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: about 6,300 KM away. Almost DELHI to LONDON!", n_at=TW + 0.2, narr_y=1560),
    dict(id="outro", s=67.5, e=72.5),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        football(frame, 540, 1400 + 12 * math.sin(T * 2), 300 * p, T)

cfg = dict(
    total=72.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("THE SUN WERE", WHITE)], 120), 770, 0.75, "right"),
        (title([("A FOOTBALL?", YEL)], 140), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Did ", WHITE), ("YOU", YEL), (" guess", WHITE)], 100), 470, 0.15),
                      (title([("6,300 km?", YEL)], 96), 600, 0.45)],
               row=[("sun", 1), ("earth", 1), ("football", 1), ("moon", 1), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.5, t1=72.5, melody=True)],
    drones=[dict(t0=39.0, dur=7.0, g=0.15)],
    fx=[("powerdown", 4.6, 0.25), ("pop", 6.9, 0.4), ("pop", 11.9, 0.3), ("whoosh", 18.8, 0.25),
        ("ding", 21.8, 0.2), ("pop", 26.3, 0.3), ("crowd", 32.3, 0.12, dict(dd=6.0)), ("ding", 49.5, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_the_sun_were_a_football")
