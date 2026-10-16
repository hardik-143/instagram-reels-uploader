#!/usr/bin/env python3
"""What if Earth were as big as Jupiter? Same rock, 11x wider -> ~11 g. Twist: real Jupiter is only ~2.6 g."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def jupiter(d, cx, cy, r, T, face=True, wink=False):
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
        for i, ex in enumerate((cx - 0.3 * r, cx + 0.05 * r)):
            if wink and i == 1:
                d.arc([ex - e, cy - 0.25 * r - e * 0.7, ex + e, cy - 0.25 * r + e * 0.7], 200, 340, fill=OUTL, width=6)
                continue
            d.ellipse([ex - e, cy - 0.25 * r - e * 1.1, ex + e, cy - 0.25 * r + e * 1.1], fill=WHITE, outline=OUTL, width=4)
            d.ellipse([ex - e * 0.45, cy - 0.25 * r - e * 0.5, ex + e * 0.45, cy - 0.25 * r + e * 0.5], fill=(25, 20, 30))
        d.arc([cx - 0.28 * r, cy - 0.12 * r, cx + 0.05 * r, cy + 0.08 * r], 20, 160, fill=OUTL, width=6)

def grow_pos(T):
    q = ease_out(clamp((T - 6.3) / 3.0))
    return (540, 1020, int(180 + 360 * q))

def size_props(frame, d, T, sc):
    q = ease_out(clamp((T - 6.3) / 3.0))
    if q < 0.95:
        jupiter(d, 860, 560, 150, T, face=False)
        l = label("JUPITER", 44, WHITE)
        comp(frame, l, 860 - l.width / 2, 730)

def weight_props(frame, d, T, sc):
    lt = T - sc["s"]
    # kid squashed: a heavy weight icon pressing down
    if lt > 1.0:
        l = label("60 KG x 11 = 660 KG", 62, YEL)
        comp(frame, l, 540 - l.width / 2, 380)

def ball_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 1.0) / 1.2)
    x = 330 + 160 * q
    y = 1060 - 260 * math.sin(math.pi * q)
    if lt >= 1.0:
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=(200, 30, 40), outline=OUTL, width=5)
        d.arc([x - 18, y - 26, x + 18, y + 26], 250, 290, fill=WHITE, width=3)
    if lt > 3.0:
        l = label("SIX = 8 M", 60, YEL)
        comp(frame, l, 540 - l.width / 2, 380)

def india_props(frame, d, T, sc):
    l = label("INDIA: NEARLY 80% OF EARTH", 56, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

def rocket_pos(T):
    lt = T - 46.0
    hop = max(0.0, math.sin(min(math.pi, lt * 1.3))) if lt > 1.0 else 0.0
    return (540, 1060 - 180 * hop, 420)

def rocket_props(frame, d, T, sc):
    l = label("NEED 120+ KM/S", 62, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp((lt - 0.2) / 0.5))
    if p > 0.02:
        jupiter(d, 540, 1040, 250 * p, T, face=True, wink=lt > 4.0)
    if lt > 2.0:
        l = label("ONLY ~2.6 G", 64, YEL)
        comp(frame, l, 540 - l.width / 2, 380)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="size", s=4.0, e=11.0, bg="space", clock="11 TIMES WIDER", char="earth", pos=grow_pos,
         props=size_props, look=(0.4, -0.2), state=lambda T: T * 12,
         narr="Jupiter is about 11 TIMES wider than Earth. Let's grow Earth to match.", n_at=4.2,
         say="Time to BULK up!", say_at=6.6, pitch=300, narr_y=1500),
    dict(id="gravity", s=11.0, e=18.0, bg="day", clock="11 G", char="uncle", state="angry",
         pos=(540, 1060, 480),
         narr="Same rock, 11 times wider: gravity gets about 11 TIMES stronger.", n_at=11.2,
         say="Who made me so HEAVY?", say_at=14.0, pitch=200, narr_y=1500),
    dict(id="weight", s=18.0, e=25.0, bg="bedroom", clock="FEELS LIKE", char="kid", state="puff",
         pos=(540, 1080, 420), props=weight_props,
         narr="A 60 KG person would feel like 660 KG. Getting out of bed? Impossible.", n_at=18.2,
         say="Mummy, I can't GET UP!", say_at=21.4, pitch=600, narr_y=1500),
    dict(id="blood", s=25.0, e=32.0, bg="speed", clock="9 G LIMIT", char="heart", pos=(540, 1060, 440),
         narr="Fighter pilots handle 9 G only BRIEFLY. At 11 G, blood struggles to reach your BRAIN.", n_at=25.2,
         say="I QUIT!", say_at=28.6, pitch=240, narr_y=1500),
    dict(id="cricket", s=32.0, e=39.0, bg="stadium", clock="CRICKET AT 11 G", char="bat", pos=(300, 1080, 360),
         props=ball_props, look=(0.6, -0.4),
         narr="A 90 M six would land only about 8 M away. Bowlers would LOVE it.", n_at=32.2,
         say="That was my BEST shot!", say_at=35.0, pitch=420, narr_y=1500),
    dict(id="india", s=39.0, e=46.0, bg="space", clock="120 TIMES THE LAND", char="earth", pos=(540, 1040, 500),
         props=india_props, look=(0, 0.2), state=lambda T: T * 12,
         narr="The surface grows about 120 TIMES. Delhi to Mumbai by road: about 15,000 KM!", n_at=39.2,
         say="Are we there YET?", say_at=42.4, pitch=300, narr_y=1500),
    dict(id="rocket", s=46.0, e=53.0, bg="space", clock="ESCAPE SPEED", char="rocket", pos=rocket_pos,
         props=rocket_props, look=(0, -0.4),
         narr="Escaping would need over 120 KM/S. Today: 11.2. No rocket could do it.", n_at=46.2,
         say="ISRO, we have a PROBLEM.", say_at=49.6, pitch=360, narr_y=1500),
    dict(id="twist", s=53.0, e=60.0, bg="space", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: real Jupiter's gravity is only about 2.6 G. It's mostly light GAS.", n_at=53.2,
         say="I'm big, but FLUFFY.", say_at=56.4, pitch=180, narr_y=1500),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        jupiter(d, 700, 1420, 150 * p, T, face=False)
        paste_c(frame, draw_char("earth", 170, T, 0, False, (0.6, 0), T * 20), 330, 1420, p)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EARTH WERE", WHITE)], 140), 770, 0.75, "right"),
        (title([("AS BIG AS", WHITE)], 140), 915, 1.05, "left"),
        (title([("JUPITER?", YEL)], 120), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Could ", WHITE), ("YOU", YEL), (" survive", WHITE)], 100), 470, 0.15),
                      (title([("at 11 G?", YEL)], 116), 600, 0.45)],
               row=[("earth", 1), ("uncle", "angry"), ("kid", "puff"), ("bat", 1), ("rocket", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0), dict(t0=25.0, t1=32.0, drums=False, minor=True),
           dict(t0=32.0, t1=52.85, melody=True), dict(t0=60.0, t1=65.0, melody=True)],
    drones=[dict(t0=53.2, dur=6.5, g=0.05)],
    fx=[("rumble", 6.3, 0.5, dict(dd=3.0)), ("boom", 11.3, 0.5), ("crash", 18.9, 0.5),
        ("heartbeat", 25.2, 0.5, dict(dd=6.5, bpm=110)), ("click", 33.0, 1.0), ("crowd", 32.3, 0.3, dict(dd=6.0)),
        ("cheer", 36.0, 0.4), ("rumble", 47.0, 0.6, dict(dd=4.0)), ("powerdown", 49.0, 0.6)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_earth_were_as_big_as_jupiter")
