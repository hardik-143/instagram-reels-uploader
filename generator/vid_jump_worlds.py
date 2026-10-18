#!/usr/bin/env python3
"""What if you jumped on other worlds? Same 0.5 m Earth jump: Moon ~3 m, Mars ~1.3 m, Venus ~same (but 465 C),
Jupiter ~20 cm, Pluto ~8 m. Twist: on comet 67P (escape speed ~1 m/s) one jump sends you into space."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

GROUND = 1330   # y of the ground line
KID = 400       # kid sprite size
REST = GROUND - KID // 2 + 10

# ---------------------------------------------------------------- world backgrounds
WORLDS = {
    #          sky gradient                                   ground col        ground dark       stars
    "moon":   ([(0, (2, 2, 12)), (1, (14, 12, 30))],          (176, 176, 186), (130, 130, 142), True),
    "mars":   ([(0, (214, 150, 104)), (1, (244, 200, 150))], (196, 92, 52),   (150, 66, 40),   False),
    "venus":  ([(0, (236, 150, 60)), (1, (255, 206, 120))],  (150, 96, 50),   (112, 70, 36),   False),
    "jupiter":([(0, (120, 80, 60)), (1, (226, 180, 130))],   (232, 196, 150), (200, 150, 104), False),
    "pluto":  ([(0, (4, 4, 16)), (1, (22, 18, 40))],          (236, 214, 200), (200, 170, 160), True),
    "comet":  ([(0, (0, 0, 6)), (1, (8, 8, 20))],             (70, 66, 64),    (44, 42, 42),    True),
}
_wcache = {}
def world(kind):
    if kind in _wcache: return _wcache[kind]
    sky, gc, gd, stars = WORLDS[kind]
    img = grad(sky, W, H); d = ImageDraw.Draw(img)
    rng = np.random.default_rng(len(kind) * 31 + 5)
    if stars:
        for _ in range(220):
            x, y = rng.uniform(0, W), rng.uniform(0, GROUND - 40)
            r = rng.choice([1.5, 2, 3])
            d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 230, 250))
    if kind == "moon":
        # Earth hanging in the black sky
        cx, cy, r = 965, 470, 80
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 140, 230), outline=OUTL, width=5)
        for dx, dy, rr in ((-30, -20, 40), (35, 30, 30), (-10, 45, 22)):
            d.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr], fill=(90, 190, 110))
    if kind == "jupiter":
        for i, y in enumerate(range(380, GROUND, 120)):
            d.rounded_rectangle([-40, y, W + 40, y + 46], radius=23, fill=(214, 160, 112) if i % 2 else (240, 214, 176))
    if kind == "venus":
        for i in range(5):
            y = 420 + i * 150
            d.rounded_rectangle([-60 + 80 * (i % 2), y, W + 60, y + 40], radius=20, fill=(255, 220, 150))
    if kind == "mars":
        # small distant Sun and a dust-coloured hill
        d.ellipse([820, 430, 870, 480], fill=(255, 250, 220))
        d.ellipse([-200, GROUND - 160, 520, GROUND + 160], fill=(176, 80, 46))
    if kind == "comet":
        # gas jets on the horizon
        for x in (180, 820):
            for k in range(6):
                d.ellipse([x - 20 - k * 14, GROUND - 120 - k * 90, x + 20 + k * 14, GROUND - 60 - k * 90],
                          fill=(70 + k * 6, 76 + k * 6, 90 + k * 6))
    # ground
    if kind == "jupiter":
        # no solid ground: thick cloud deck
        for x in range(-60, W + 120, 130):
            d.ellipse([x - 90, GROUND - 50, x + 90, GROUND + 70], fill=gc)
        d.rectangle([0, GROUND + 10, W, H], fill=gc)
    else:
        d.rectangle([0, GROUND, W, H], fill=gc)
        d.line([(0, GROUND), (W, GROUND)], fill=gd, width=6)
        for _ in range(26):
            x, y = rng.uniform(0, W), rng.uniform(GROUND + 30, H - 40)
            rw = rng.uniform(20, 70)
            if kind in ("moon", "pluto", "comet"):
                d.ellipse([x - rw, y - rw * 0.35, x + rw, y + rw * 0.35], fill=gd)
            else:
                d.ellipse([x - rw * 0.5, y - rw * 0.25, x + rw * 0.5, y + rw * 0.25], fill=gd)
    if kind == "pluto":
        # the famous pale "heart" patch
        hx, hy = 760, GROUND + 140
        d.ellipse([hx - 120, hy - 70, hx, hy + 30], fill=(250, 240, 232))
        d.ellipse([hx - 20, hy - 70, hx + 100, hy + 30], fill=(250, 240, 232))
        d.polygon([(hx - 116, hy - 10), (hx + 96, hy - 10), (hx - 10, hy + 110)], fill=(250, 240, 232))
    _wcache[kind] = img
    return img

def wbg(kind):
    return lambda T: world(kind)

# ---------------------------------------------------------------- jumping kid
def jumper(t0, height_px, air, x=540, repeat=None):
    """Kid crouches, jumps to height_px over `air` seconds, lands. Optional repeat period."""
    def pos(T):
        lt = T - t0
        if repeat and lt > 0: lt = lt % repeat
        y = REST
        if 0 <= lt < air:
            q = lt / air
            y = REST - height_px * 4 * q * (1 - q)
        elif -0.25 <= lt < 0 or air <= lt < air + 0.2:
            y = REST + 14   # crouch / landing squash
        return (x, y, KID)
    return pos

def shadow_props(x, t0, height_px, air, repeat=None, extra=None):
    def f(frame, d, T, sc):
        lt = T - t0
        if repeat and lt > 0: lt = lt % repeat
        h = height_px * 4 * (lt / air) * (1 - lt / air) if 0 <= lt < air else 0
        sh = Image.new("RGBA", (W, 80), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        s = max(0.35, 1 - h / 700)
        sd.ellipse([x - 110 * s, 40 - 14 * s, x + 110 * s, 40 + 14 * s], fill=(0, 0, 0, 80))
        comp(frame, sh, 0, GROUND - 40)
        if extra: extra(frame, d, T, sc)
    return f

def hot_props(frame, d, T, sc):
    lt = T - sc["s"]
    # heat shimmer
    for k in range(7):
        x = 90 + k * 150; y = 1200 - ((lt * 120 + k * 60) % 300)
        d.arc([x - 30, y - 20, x + 30, y + 20], 200, 340, fill=(255, 120, 40), width=6)

def twist_pos(T):
    lt = T - 46.0
    if lt < 1.0: return (540, REST + (14 if lt > 0.75 else 0), KID)
    q = lt - 1.0
    y = REST - 260 * q - 30 * q * q
    s = max(60, int(KID * (1 - 0.1 * q)))
    return (540, y, s)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 4.2:
        l = label("ESCAPE SPEED ~1 M/S", 58, YEL)
        comp(frame, l, 540 - l.width / 2, 380)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="earth", s=4.0, e=11.0, bg="day", clock="EARTH", char="kid", pos=jumper(5.0, 45, 0.64, repeat=1.6),
         props=shadow_props(540, 5.0, 45, 0.64, repeat=1.6),
         narr="On Earth, a good jump lifts you about HALF a metre. Air time: under 1 SECOND.", n_at=4.2,
         say="Boring. Take me to SPACE!", say_at=7.6, pitch=600, bubble_y=600),
    dict(id="moon", s=11.0, e=18.0, bg_fn=wbg("moon"), clock="MOON · 1/6 GRAVITY", char="kid",
         pos=jumper(12.0, 300, 3.9), props=shadow_props(540, 12.0, 300, 3.9),
         narr="Moon gravity is about 1/6 of Earth's. Same jump: about 3 METRES, 4 SECONDS up.", n_at=11.2,
         say="Hi, PRAGYAN rover!", say_at=14.6, pitch=620, bubble_y=600, look=(0.4, -0.4)),
    dict(id="mars", s=18.0, e=25.0, bg_fn=wbg("mars"), clock="MARS · 38% GRAVITY", char="kid",
         pos=jumper(18.9, 130, 1.7, repeat=2.6), props=shadow_props(540, 18.9, 130, 1.7, repeat=2.6),
         narr="Mars pulls about 38% as hard. You'd clear about 1.3 METRES.", n_at=18.2,
         say="Basketball team, PICK ME!", say_at=21.0, pitch=600, bubble_y=600),
    dict(id="venus", s=25.0, e=32.0, bg_fn=wbg("venus"), clock="VENUS · 90% GRAVITY", char="kid", state="puff",
         pos=(540, REST, KID), props=hot_props,
         narr="Venus gravity is close to ours, so same jump. But the ground is about 465°C.", n_at=25.2,
         say="Too HOT to jump!", say_at=28.6, pitch=640, bubble_y=600),
    dict(id="jupiter", s=32.0, e=39.0, bg_fn=wbg("jupiter"), clock="JUPITER · 2.4X GRAVITY", char="kid",
         pos=jumper(33.0, 20, 0.42, repeat=1.2), props=shadow_props(540, 33.0, 20, 0.42, repeat=1.2),
         narr="Jupiter has no solid ground. At its cloud tops, gravity is about 2.4 TIMES ours: a 20 CM hop.", n_at=32.2,
         say="My legs feel like CEMENT!", say_at=35.4, pitch=560, bubble_y=600),
    dict(id="pluto", s=39.0, e=46.0, bg_fn=wbg("pluto"), clock="PLUTO · 1/16 GRAVITY", char="kid",
         pos=jumper(39.8, 470, 6.0), props=shadow_props(540, 39.8, 470, 6.0), look=(0, -0.4),
         narr="Pluto: about 8 METRES high, taller than a 2-storey house, and 10 SECONDS in the air.", n_at=39.2),
    dict(id="twist", s=46.0, e=53.0, bg_fn=wbg("comet"), clock="COMET 67P", char="kid", pos=twist_pos,
         props=twist_props, twist=True, look=(0, -0.5),
         narr="Twist: on COMET 67P, one jump is faster than its escape speed. You'd NEVER come down.", n_at=46.2),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        hop = 60 * abs(math.sin((T - 1.9) * 3.0))
        paste_c(frame, draw_char("kid", 260, T, 0, False, (0, -0.3), 1), 540, 1440 - hop, p)

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU JUMPED", WHITE)], 140), 770, 0.75, "right"),
        (title([("ON OTHER", WHITE)], 140), 915, 1.05, "left"),
        (title([("WORLDS?", YEL)], 130), 1065, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Where would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("jump first?", YEL)], 116), 600, 0.45)],
               row=[("kid", 1), ("earth", 1), ("moon", 1), ("rocket", 1), ("sun", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=32.0, drums=False, minor=True), dict(t0=32.0, t1=45.85, melody=True),
           dict(t0=53.0, t1=58.0, melody=True)],
    drones=[dict(t0=46.2, dur=6.5, g=0.05)],
    fx=[("pop", 5.0, 0.5), ("pop", 6.6, 0.5), ("whoosh", 12.0, 0.5), ("pop", 15.9, 0.6), ("whoosh", 18.9, 0.4),
        ("pop", 20.6, 0.5), ("gasp", 26.0, 0.5), ("crash", 33.4, 0.3), ("whoosh", 39.8, 0.6),
        ("pop", 45.8, 0.6), ("whoosh", 47.0, 0.7), ("powerdown", 48.5, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_jumped_on_other_worlds")
