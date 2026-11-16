#!/usr/bin/env python3
"""What if you walked inside a cloud? Facts: fog is essentially a cloud at ground level, visibility under 1,000 m; radiation
fog forms on clear, calm winter nights (Met Office 'What is fog?'). IMD fog classes: very dense 0-50 m, dense 51-200 m,
moderate 201-500 m, shallow 501-1,000 m (Business Standard quoting IMD). Dense fog hit Delhi, Haryana and Chandigarh on
9 Nov 2026 (Down To Earth daily weather tracker). Cloud droplets average about 20 micrometres (0.02 mm) across, fall
about 1 cm/s, and about 1 million make one 2 mm raindrop (Univ. of Hawaii 'Atmospheric Processes', ch. 7). A 1 km^3
cumulus with ~0.5 g of water per m^3 holds about 500,000 kg = 500 tonnes (USGS Water Science School), ~100 elephants
at ~5 t each. A 4 x 4 x 3 m bedroom (48 m^3) of such cloud holds about 25 g. Twist: visible breath on a cold day is
water vapour condensing into tiny droplets, a little cloud/fog (Science Notes)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 46.0
FOG = (226, 230, 236)
DROP = (120, 190, 255)

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

def fog_layer(frame, T, alpha=150, n=9, y0=500, y1=1500, speed=60, seed=4):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rng = np.random.default_rng(seed)
    for k in range(n):
        y = y0 + (y1 - y0) * k / max(1, n - 1)
        x = (rng.uniform(0, W) + T * speed * (0.6 + 0.4 * (k % 3))) % (W + 600) - 300
        for dx, r in ((-160, 120), (0, 170), (160, 120), (320, 100)):
            d.ellipse([x + dx - r, y - r * 0.45, x + dx + r, y + r * 0.45], fill=FOG + (alpha,))
    frame.alpha_composite(L)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def street_bg(T):
    if "street" not in _cache:
        img = E.grad([(0, (176, 184, 196)), (1, (214, 218, 224))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        x = -20; rng = np.random.default_rng(8)
        while x < W:
            bw = int(rng.integers(140, 220)); top = int(rng.integers(820, 1060))
            d.rectangle([x, top, x + bw, 1330], fill=(168, 172, 182))
            for yy in range(top + 40, 1300, 90):
                for xx in range(x + 30, x + bw - 40, 70):
                    d.rectangle([xx, yy, xx + 34, yy + 44], fill=(190, 194, 202))
            x += bw + 14
        d.rectangle([0, 1330, W, H], fill=(140, 140, 146))
        for xx in range(40, W, 200):
            d.rectangle([xx, 1600, xx + 110, 1620], fill=(200, 200, 200))
        # soft haze over the buildings
        haze = Image.new("RGBA", (W, H), FOG + (120,))
        img.alpha_composite(haze)
        _cache["street"] = img
    img = _cache["street"].copy()
    fog_layer(img, T, alpha=110, n=7, y0=700, y1=1400, speed=40)
    return img

def rail_bg(T):
    if "rail" not in _cache:
        img = E.grad([(0, (180, 186, 196)), (1, (214, 218, 224))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1330, W, H], fill=(150, 146, 140))
        for x in range(-40, W + 40, 70):
            d.rectangle([x, 1360, x + 26, 1470], fill=(120, 96, 76))
        d.rectangle([0, 1380, W, 1392], fill=(110, 110, 120))
        d.rectangle([0, 1440, W, 1452], fill=(110, 110, 120))
        _cache["rail"] = img
    return _cache["rail"].copy()

def white_bg(T):
    if "white" not in _cache:
        _cache["white"] = E.grad([(0, (196, 206, 222)), (1, (232, 236, 242))], W, H).convert("RGBA")
    img = _cache["white"].copy()
    fog_layer(img, T, alpha=90, n=8, y0=500, y1=1600, speed=30, seed=9)
    return img

def sky_bg(T):
    if "sky" not in _cache:
        img = E.grad([(0, (110, 170, 240)), (1, (190, 225, 255))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1400, W, H], fill=(120, 190, 100))
        d.line([(0, 1400), (W, 1400)], fill=OUTL, width=6)
        _cache["sky"] = img
    return _cache["sky"]

def room_bg(T):
    if "room" not in _cache:
        img = E.grad([(0, (190, 170, 210)), (1, (220, 200, 230))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([640, 560, 980, 900], radius=12, fill=(150, 160, 190), outline=OUTL, width=6)
        d.line([(810, 560), (810, 900)], fill=OUTL, width=6)
        d.rectangle([0, 1330, W, H], fill=(150, 110, 90))
        d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
        d.rounded_rectangle([40, 1190, 560, 1340], radius=30, fill=(90, 120, 200), outline=OUTL, width=6)
        d.ellipse([70, 1150, 270, 1230], fill=(236, 236, 250), outline=OUTL, width=5)
        _cache["room"] = img
    img = _cache["room"].copy()
    fog_layer(img, T, alpha=80, n=6, y0=600, y1=1300, speed=25, seed=2)
    return img

def cold_bg(T):
    if "cold" not in _cache:
        img = E.grad([(0, (150, 190, 230)), (1, (225, 236, 248))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1330, W, H], fill=(200, 210, 222))
        d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)
        _cache["cold"] = img
    return _cache["cold"]

# ---------------------------------------------------------------- props
def fog_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "FOG = CLOUD ON THE GROUND", 380, YEL, 60)

def fog_front(frame, d, T, sc):
    fog_layer(frame, T, alpha=70, n=4, y0=1000, y1=1350, speed=80, seed=7)

def train_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.3) / 5.5))
    tx = 1300 - 480 * g
    spr = draw_char("train", 560, T, 0.0, False, (-0.6, 0), 1)
    comp(frame, spr, tx - spr.width / 2, 1110 - spr.height / 2)
    # very thick fog in front of the train
    fog_layer(frame, T, alpha=150, n=5, y0=850, y1=1350, speed=30, seed=3)
    if lt > 0.5:
        top_label(frame, "VERY DENSE: UNDER 50 M", 380, YEL, 72)

def drop_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = min(ease_back(clamp((lt - 0.3) / 0.6)), 1.08)
    cx, cy, r = 700, 1000, 250 * g
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 246, 255), outline=OUTL, width=12)
    d.line([(cx - r * 0.7, cy + r * 0.7), (cx - r * 1.25, cy + r * 1.25)], fill=OUTL, width=26)
    rng = np.random.default_rng(12)
    for k in range(int(26 * g)):
        a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0, 0.8) * r
        x = cx + rr * math.cos(a) + 6 * math.sin(T * 3 + k); y = cy + rr * math.sin(a) + 6 * math.cos(T * 2 + k)
        s = 14
        d.ellipse([x - s, y - s, x + s, y + s], fill=DROP, outline=OUTL, width=3)
    if lt > 0.5:
        top_label(frame, "EACH DROP: 0.02 MM", 380, YEL, 84)
    if lt > 3.0:
        # one raindrop = a million droplets
        rx, ry = 230, 860
        d.polygon([(rx, ry - 70), (rx + 46, ry + 10), (rx - 46, ry + 10)], fill=DROP, outline=OUTL)
        d.ellipse([rx - 48, ry - 30, rx + 48, ry + 60], fill=DROP, outline=OUTL, width=5)
        at_label(frame, "1 RAINDROP =", rx, ry + 105, WHITE, 40)
        at_label(frame, "1,000,000 OF THEM", rx, ry + 155, YEL, 40)

def fall_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a single droplet sinking very slowly, nudged up by rising air
    x, y = 760, 860 + 18 * lt + 20 * math.sin(T * 2)
    d.ellipse([x - 60, y - 60, x + 60, y + 60], fill=DROP, outline=OUTL, width=6)
    d.ellipse([x - 30, y - 34, x - 10, y - 14], fill=WHITE)
    for k in range(4):
        ph = (lt * 0.9 + k / 4) % 1
        yy = 1300 - 360 * ph
        xx = 640 + k * 80
        d.line([(xx, yy), (xx, yy - 70)], fill=WHITE, width=8)
        d.polygon([(xx - 18, yy - 60), (xx + 18, yy - 60), (xx, yy - 90)], fill=WHITE)
    if lt > 0.5:
        top_label(frame, "FALL SPEED: 1 CM/SEC", 380, YEL, 76)
    if lt > 2.0:
        at_label(frame, "RISING AIR", 760, 1360, WHITE, 46)

def elephant(d, x, y, s):
    g = (150, 150, 160)
    d.ellipse([x - 50 * s, y - 34 * s, x + 50 * s, y + 30 * s], fill=g, outline=OUTL, width=max(2, int(4 * s)))
    for lx in (-34, -12, 14, 34):
        d.rectangle([x + lx * s - 8 * s, y + 10 * s, x + lx * s + 8 * s, y + 52 * s], fill=g, outline=OUTL,
                    width=max(1, int(3 * s)))
    d.ellipse([x + 32 * s, y - 52 * s, x + 82 * s, y - 2 * s], fill=g, outline=OUTL, width=max(2, int(4 * s)))
    d.ellipse([x + 24 * s, y - 44 * s, x + 50 * s, y - 6 * s], fill=(175, 170, 180), outline=OUTL, width=max(1, int(3 * s)))
    d.line([(x + 76 * s, y - 20 * s), (x + 86 * s, y + 22 * s), (x + 78 * s, y + 40 * s)], fill=OUTL,
           width=max(3, int(9 * s)))
    d.ellipse([x + 60 * s, y - 36 * s, x + 68 * s, y - 28 * s], fill=OUTL)

def weight_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = int(clamp((lt - 1.0) / 3.0) * 8)
    for k in range(n):
        x = 150 + (k % 4) * 250; y = 1200 + (k // 4) * 130
        elephant(d, x, y, 1.0)
    if lt > 0.5:
        top_label(frame, "500 TONNES OF WATER", 380, YEL, 80)
    if lt > 4.0:
        at_label(frame, "= ABOUT 100 ELEPHANTS", 540, 1100, WHITE, 58)

def cloud_pos(T):
    return (540, 860 + 14 * math.sin(T * 1.5), 520)

def room_props(frame, d, T, sc):
    lt = T - sc["s"]
    # small glass on a side table
    d.rectangle([700, 1180, 960, 1200], fill=(140, 100, 70), outline=OUTL, width=5)
    d.rectangle([730, 1200, 750, 1330], fill=(140, 100, 70)); d.rectangle([910, 1200, 930, 1330], fill=(140, 100, 70))
    gx, gy = 830, 1180
    d.polygon([(gx - 50, gy - 150), (gx + 50, gy - 150), (gx + 40, gy), (gx - 40, gy)], fill=(235, 245, 255),
              outline=OUTL)
    f = ease_out(clamp((lt - 1.0) / 2.0))
    d.polygon([(gx - 42, gy - 30 * f), (gx + 42, gy - 30 * f), (gx + 40, gy), (gx - 40, gy)], fill=DROP)
    if lt > 1.5:
        at_label(frame, "ABOUT 25 G", gx, gy - 210, WHITE, 52)
    if lt > 0.5:
        top_label(frame, "A ROOM FULL OF CLOUD", 380, YEL, 78)

def breath_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(5):
        ph = (lt * 0.5 + k / 5) % 1
        x = 510 + 380 * ph; y = 1195 - 170 * ph + 10 * math.sin(T * 3 + k)
        r = 40 + 120 * ph
        a = int(245 * (1 - ph) ** 0.7)
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(255, 255, 255, a), outline=(150, 170, 200, a), width=4)
        frame.alpha_composite(L)
    if lt > 0.5:
        top_label(frame, "YOUR BREATH = MINI CLOUD", 380, YEL, 70)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="fog", s=4.0, e=11.0, bg_fn=street_bg, clock="WINTER MORNING", char="kid", state="puff",
         pos=(540, 1130, 380), props=fog_props, props_after=fog_front, look=(0.3, -0.2),
         narr="North India's winter FOG is really a CLOUD sitting on the ground.", n_at=4.2, narr_y=1560,
         say="I'm walking IN a cloud!", say_at=7.2, pitch=440),
    dict(id="see", s=11.0, e=18.0, bg_fn=rail_bg, clock="STATION", char="uncle", pos=(230, 1150, 340),
         props=train_props, look=(0.6, 0),
         narr="IMD calls it VERY DENSE fog when you can't see even 50 METRES.", n_at=11.2, narr_y=1560,
         say="Train late AGAIN?!", say_at=14.4, pitch=150),
    dict(id="drop", s=18.0, e=25.0, bg_fn=white_bg, clock="ZOOM IN", char="kid", pos=(250, 1250, 260),
         props=drop_props, look=(0.6, -0.3),
         narr="Each droplet is about 0.02 MM wide. About a MILLION make one raindrop.", n_at=18.2,
         narr_y=1560, say="Tiny water PIXELS!", say_at=21.6, pitch=440),
    dict(id="fall", s=25.0, e=32.0, bg_fn=white_bg, clock="WHY NO RAIN?", char="kid", pos=(280, 1150, 340),
         props=fall_props, look=(0.6, -0.2),
         narr="They fall only about 1 CM a second, so gentle rising air keeps them UP.", n_at=25.2,
         narr_y=1560, say="Slowest fall EVER!", say_at=28.4, pitch=440),
    dict(id="weight", s=32.0, e=39.0, bg_fn=sky_bg, clock="WEIGH-IN", char="cloud", pos=cloud_pos,
         props=weight_props, look=(0, 0.4),
         narr="A puffy cloud 1 KM on each side holds about 500 TONNES of water.", n_at=32.2, narr_y=1560,
         say="Not fat, just FLUFFY!", say_at=35.6, pitch=360),
    dict(id="room", s=39.0, e=TW, bg_fn=room_bg, clock="BUT WAIT", char="kid", pos=(300, 1060, 300),
         props=room_props, look=(0.6, 0.2),
         narr="But it's spread thin. A bedroom full of cloud holds about 25 GRAMS.", n_at=39.2,
         narr_y=1560, say="That's a few SIPS!", say_at=42.4, pitch=440),
    dict(id="twist", s=TW, e=54.0, bg_fn=cold_bg, clock="PLOT TWIST", char="kid", state="puff",
         pos=(440, 1130, 380), props_after=breath_props, twist=True, look=(0.6, -0.1),
         narr="Twist: on a cold morning, every breath you puff out is a tiny CLOUD.",
         n_at=TW + 0.2, narr_y=1560, say="I'm a CLOUD FACTORY!", say_at=TW + 3.4, pitch=440),
    dict(id="outro", s=54.0, e=59.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.15)
        spr = draw_char("cloud", int(360 * p) + 2, T, 0.0, False, (0, 0), 1)
        comp(frame, spr, 540 - spr.width / 2, 1400 - spr.height / 2 + 12 * math.sin(T * 2))

cfg = dict(
    total=59.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU WALKED", WHITE)], 120), 770, 0.75, "right"),
        (title([("INSIDE A CLOUD?", YEL)], 120), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" walk", WHITE)], 100), 470, 0.15),
                      (title([("into a cloud?", YEL)], 96), 600, 0.45)],
               row=[("cloud", 1), ("kid", 1), ("train", 1), ("chai", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, drums=False, minor=True),
           dict(t0=18.0, t1=32.0, melody=True), dict(t0=32.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=59.0, melody=True)],
    drones=[dict(t0=4.0, dur=14.0, g=0.2)],
    fx=[("wind", 4.3, 0.25, dict(dd=6.0)), ("whistle", 11.6, 0.25), ("rumble", 12.0, 0.25, dict(dd=4.0)),
        ("pop", 18.6, 0.25), ("bubbles", 21.2, 0.2), ("wind", 25.4, 0.2, dict(dd=5.0)), ("boom", 32.6, 0.2),
        ("pop", 33.5, 0.2), ("pop", 34.4, 0.2), ("pop", 35.3, 0.2), ("ding", 41.0, 0.25), ("wind", TW + 0.5, 0.2, dict(dd=6.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_walked_inside_a_cloud")
