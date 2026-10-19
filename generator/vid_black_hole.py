#!/usr/bin/env python3
"""What if you fell into a black hole? Nearest known (Gaia BH1) ~1,560 ly; EHT shadow photo 2019; small black
holes spaghettify you, a giant one (Sgr A*, ~4 million Suns) lets you cross intact; a distant friend sees you
freeze and fade; escaping would need more than light speed; Chandrasekhar + NASA's Chandra.
Twist: Earth squeezed into a black hole would be only ~2 cm wide, smaller than a ladoo."""
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

_gl = {}
def glow_spr(r, col, strength=0.8, ring=False):
    k = (int(r), col, round(strength, 2), ring)
    if k not in _gl:
        R = int(r)
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        dist = np.sqrt(xx ** 2 + yy ** 2) / R
        if ring:   # bright ring peaking at 0.62 R
            q = np.clip(1 - np.abs(dist - 0.62) / 0.38, 0, 1) ** 1.6
        else:
            q = np.clip(1 - dist, 0, 1) ** 2
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (q * 255 * strength).astype(np.uint8)
        _gl[k] = Image.fromarray(arr, "RGBA")
    return _gl[k]

def blackhole(frame, cx, cy, r, T, spin=True):
    """EHT-style: glowing orange ring (brighter on one side) around a black shadow."""
    ring = glow_spr(r * 1.9, (255, 150, 50), 1.0, ring=True)
    frame.alpha_composite(ring, (int(cx - ring.width / 2), int(cy - ring.height / 2)))
    hot = glow_spr(r * 0.9, (255, 230, 150), 0.7)
    a = T * 0.8 if spin else 0
    hx, hy = cx + math.cos(a) * r * 0.75, cy + math.sin(a) * r * 0.75 + r * 0.25
    frame.alpha_composite(hot, (int(hx - hot.width / 2), int(hy - hot.height / 2)))
    d = ImageDraw.Draw(frame)
    d.ellipse([cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82], fill=(0, 0, 0))

def bh_bg_fn(cx=540, cy=640, r=230):
    cache = {}
    def f(T):
        key = int(T * 15)
        if key not in cache:
            img = E.bg("space").copy()
            blackhole(img, cx, cy, r, key / 15)
            cache.clear(); cache[key] = img
        return cache[key]
    return f

# ---------------------------------------------------------------- scenes
def trip_props(frame, d, T, sc):
    lt = T - sc["s"]
    blackhole(frame, 860, 470, 70, T)
    l = label("GAIA BH1", 44, WHITE); comp(frame, l, 860 - l.width / 2, 590)
    d.ellipse([140, 1270, 220, 1350], fill=(80, 150, 230), outline=OUTL, width=4)
    if lt > 1.0:
        l = label("~1,560 LIGHT-YEARS", 54, YEL); comp(frame, l, 470 - l.width / 2, 700)

def shadow_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.2:
        l = label("FIRST PHOTO: 2019", 56, YEL); comp(frame, l, 540 - l.width / 2, 360)

def stretch_after(frame, d, T, sc):
    lt = T - sc["s"]
    q = ease_out(clamp((lt - 0.8) / 2.5))
    sx, sy = 1 - 0.55 * q, 1 + 1.4 * q
    B = 300
    spr = draw_char("kid", B, T, 0, False, (0, -0.5), "puff" if q > 0.3 else 1)
    spr = spr.resize((max(1, int(B * sx)), max(1, int(B * sy))), Image.BICUBIC)
    cy = 1100 - 200 * q
    comp(frame, spr, 540 - spr.width / 2, cy - spr.height / 2)
    if lt > 3.2:
        l = label("SPAGHETTIFICATION", 58, YEL); comp(frame, l, 540 - l.width / 2, 360)

def giant_props(frame, d, T, sc):
    lt = T - sc["s"]
    l = label("SGR A*: ~4 MILLION SUNS", 54, YEL)
    if 1.0 < lt < 3.3: comp(frame, l, 540 - l.width / 2, 360)
    elif lt > 5.5: comp(frame, l, 540 - l.width / 2, 1010)

def giant_pos(T):
    lt = T - 25.0
    q = ease_out(clamp((lt - 2.0) / 4.5))
    return (540, 1120 - 380 * q, int(340 - 120 * q))

def friend_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 0.5) / 5.0)
    B = 260
    spr = draw_char("kid", B, 30.0 + 0.3 * q, 0, False, (0, -0.4), 1)   # time slows down: pose freezes
    tint = Image.new("RGBA", spr.size, (220, 40, 30, 0))
    arr = np.array(spr).astype(np.float32)
    arr[..., 1] *= (1 - 0.7 * q); arr[..., 2] *= (1 - 0.8 * q)
    arr[..., 3] *= (1 - 0.6 * q)
    spr = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    x = 540 + 40 * math.sin(min(q, 0.4) * 8)
    comp(frame, spr, 300 - B / 2 + 40 * (1 - q), 1010 - B / 2)

def escape_pos(T):
    lt = T - 39.0
    shake = 6 * math.sin(T * 40) if lt > 2.0 else 0
    return (540 + shake, 1080 + 40 * clamp((lt - 2.0) / 4.0), 340)

def escape_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0:
        l = label("NEED > 300,000 KM/S", 56, YEL); comp(frame, l, 540 - l.width / 2, 360)

def chandra_props(frame, d, T, sc):
    lt = T - sc["s"]
    # simple space telescope
    cx, cy = 300, 640
    d.rounded_rectangle([cx - 150, cy - 40, cx + 110, cy + 40], radius=18, fill=(220, 220, 230), outline=OUTL, width=5)
    d.rectangle([cx + 110, cy - 30, cx + 150, cy + 30], fill=(170, 170, 185), outline=OUTL, width=4)
    for sx in (-1, 1):
        y0, y1 = sorted((cy + sx * 50, cy + sx * 150))
        d.rectangle([cx - 110, y0, cx - 20, y1], fill=(60, 90, 190), outline=OUTL, width=4)
        d.line([(cx - 65, cy + sx * 50), (cx - 65, cy + sx * 150)], fill=(140, 170, 240), width=3)
    if lt > 1.0:
        l = label("NASA's CHANDRA", 54, YEL); comp(frame, l, 300 - l.width / 2, 400)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp((lt - 0.8) / 0.4))
    if p > 0.02:
        cx, cy, r = 820, 1090, 16 * p
        g = glow_spr(48 * p + 2, (255, 160, 60), 0.9, ring=True)
        frame.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0))
        l = label("EARTH", 44, WHITE); comp(frame, l, cx - l.width / 2, cy + 60)
    if lt > 1.6:
        l = label("~2 CM WIDE", 66, YEL); comp(frame, l, 540 - l.width / 2, 400)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="trip", s=4.0, e=11.0, bg="space", clock="NEAREST KNOWN", char="rocket", pos=(420, 1010, 330),
         props=trip_props, look=(0.6, -0.4),
         narr="The nearest known black hole, GAIA BH1, is about 1,560 LIGHT-YEARS away.", n_at=4.2,
         say="Long trip. Pack SAMOSAS.", say_at=7.4, pitch=360, bubble_y=880),
    dict(id="shadow", s=11.0, e=18.0, bg_fn=bh_bg_fn(), clock="FIRST LOOK", char="kid", pos=(540, 1150, 300),
         props=shadow_props, look=(0, -0.6),
         narr="Up close: a black SHADOW in a ring of glowing gas. Scientists first PHOTOGRAPHED one in 2019.",
         n_at=11.2, say="A cosmic DONUT!", say_at=14.4, pitch=620, bubble_y=1000),
    dict(id="small", s=18.0, e=25.0, bg_fn=bh_bg_fn(540, 520, 150), clock="SMALL BLACK HOLE", props_after=stretch_after,
         narr="A small one would STRETCH you like a noodle. Scientists call it SPAGHETTIFICATION.", n_at=18.2),
    dict(id="giant", s=25.0, e=32.0, bg_fn=bh_bg_fn(540, 640, 330), clock="GIANT BLACK HOLE", char="kid",
         pos=giant_pos, props=giant_props, look=(0, -0.6),
         narr="Pick a GIANT one, like the monster at our galaxy's centre. You'd cross the edge in ONE piece.",
         n_at=25.2, say="Phew, still ME!", say_at=28.6, pitch=620, bubble_y=530),
    dict(id="friend", s=32.0, e=39.0, bg_fn=bh_bg_fn(330, 640, 200), clock="YOUR FRIEND'S VIEW", char="uncle",
         pos=(820, 1110, 300), props=friend_props, look=(-0.6, -0.4),
         narr="A friend watching from far away would see you SLOW down, FREEZE and fade to red.", n_at=32.2,
         say="Beta, why so SLOW?", say_at=35.4, pitch=200, bubble_y=840),
    dict(id="escape", s=39.0, e=46.0, bg_fn=bh_bg_fn(540, 560, 260), clock="NO WAY BACK", char="rocket",
         pos=escape_pos, props=escape_props, look=(0, -0.5),
         narr="Inside the EVENT HORIZON, escape needs more than LIGHT speed. Nothing can do that.", n_at=39.2,
         say="Full power... still STUCK!", say_at=42.2, pitch=360, bubble_y=850),
    dict(id="chandra", s=46.0, e=53.0, bg="space", clock="INDIAN CONNECTION", char="moon", pos=(760, 1080, 300),
         props=chandra_props, look=(-0.6, -0.4),
         narr="India-born CHANDRASEKHAR showed big stars can end as BLACK HOLES. NASA's CHANDRA honours him.", narr_y=1440,
         n_at=46.2, say="Chandra means MOON!", say_at=49.6, pitch=380, bubble_y=880),
    dict(id="twist", s=53.0, e=60.0, bg="twist", clock="PLOT TWIST", char="ladoo", pos=(420, 1080, 380),
         props=twist_props, twist=True, look=(0.6, 0),
         narr="Twist: squeeze EARTH into a black hole and it'd be about 2 CM wide. Smaller than a LADOO.", n_at=53.2,
         say="I'm BIGGER than Earth!", say_at=56.4, pitch=420, bubble_y=780),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back(clamp((T - 1.9) / 0.4))
        if p > 0.05: blackhole(frame, 540, 1440, 150 * p, T)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU FELL", WHITE)], 140), 720, 0.75, "right"),
        (title([("INTO A", WHITE)], 140), 865, 1.05, "left"),
        (title([("BLACK HOLE?", YEL)], 130), 1015, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" jump in?", WHITE)], 100), 470, 0.15),
                      (title([("Small or giant?", YEL)], 104), 600, 0.45)],
               row=[("kid", 1), ("rocket", 1), ("moon", 1), ("uncle", "hat"), ("ladoo", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=25.0, drums=False, minor=True), dict(t0=25.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0, drums=False, minor=True), dict(t0=46.0, t1=52.85, melody=True),
           dict(t0=60.0, t1=65.0, melody=True)],
    drones=[dict(t0=11.2, dur=6.5, g=0.04), dict(t0=53.2, dur=6.5, g=0.05)],
    fx=[("rumble", 4.5, 0.4, dict(dd=3.0)), ("whoosh", 18.8, 0.6), ("screech", 20.0, 0.3), ("gasp", 21.5, 0.4),
        ("whoosh", 27.0, 0.5), ("powerdown", 33.0, 0.5), ("rumble", 41.0, 0.6, dict(dd=4.0)), ("ding", 47.2, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_fell_into_a_black_hole")
