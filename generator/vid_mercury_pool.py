#!/usr/bin/env python3
"""What if you jumped into a pool of mercury? Mercury: only metal liquid at standard conditions, density 13.534 g/cm3,
melts at -38.83 C (New World Encyclopedia / LibreTexts B7). 10 L ~ 135 kg. A ~1 g/cm3 body floats with ~1/13.5 = ~7%
submerged (Archimedes). Iron 7.87, silver 10.5 float; gold 19.3 sinks and dissolves (amalgam). Safety: WHO lists
mercury among its top ten chemicals of major public health concern; mercury vapour harms the nervous system."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

SURF = 1250   # mercury surface y

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

# ---------------------------------------------------------------- background
_cache = {}
def merc_bg():
    if "m" not in _cache:
        y = np.linspace(0, 1, H)[:, None]
        top = np.array([236, 246, 252]); bot = np.array([214, 232, 244])
        a = (top * (1 - y[..., None]) + bot * y[..., None]).astype(np.uint8)
        a = np.broadcast_to(a, (H, W, 3)).copy()
        img = Image.fromarray(a).convert("RGBA"); d = ImageDraw.Draw(img)
        for yy in range(0, SURF - 40, 70): d.line([(0, yy), (W, yy)], fill=(210, 226, 236), width=3)
        for xx in range(0, W, 70): d.line([(xx, 0), (xx, SURF - 40)], fill=(210, 226, 236), width=3)
        # ladder
        for x in (900, 980):
            d.line([(x, SURF - 260), (x, SURF + 40)], fill=(170, 176, 186), width=12)
            d.arc([x, SURF - 300, x + 80, SURF - 220], 180, 360, fill=(170, 176, 186), width=12)
        for yy in range(SURF - 220, SURF, 60): d.line([(900, yy), (980, yy)], fill=(170, 176, 186), width=8)
        d.rectangle([0, SURF - 40, W, SURF], fill=(250, 250, 250))
        # liquid metal, darker with depth
        for i in range(H - SURF):
            q = i / (H - SURF)
            c = (int(214 - 110 * q), int(218 - 108 * q), int(228 - 100 * q))
            d.line([(0, SURF + i), (W, SURF + i)], fill=c)
        rng = np.random.default_rng(7)
        for _ in range(26):
            x, yy = rng.uniform(0, W), rng.uniform(SURF + 30, H)
            d.line([(x, yy), (x + rng.uniform(60, 160), yy + 4)], fill=(245, 248, 255), width=5)
        _cache["m"] = img
    return _cache["m"]

def mbg(T): return merc_bg()

def surface_front(d, T, x0=0, x1=W):
    """Redraw the top band of the metal over a character so it looks partly sunk."""
    for i in range(70):
        q = i / (H - SURF)
        c = (int(214 - 110 * q), int(218 - 108 * q), int(228 - 100 * q))
        d.line([(x0, SURF + i), (x1, SURF + i)], fill=c)
    for k in range(4):
        x = (k * 260 + T * 40) % (W + 200) - 100
        d.line([(x, SURF + 20), (x + 120, SURF + 22)], fill=(245, 248, 255), width=5)

# ---------------------------------------------------------------- props
def meet_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 3.2:
        top_label(frame, "LIQUID METAL", 380, YEL, 76)

def bucket(d, x, y, s=1.0):
    c = lambda v: v * s
    d.polygon([(x - c(110), y - c(120)), (x + c(110), y - c(120)), (x + c(85), y + c(120)), (x - c(85), y + c(120))],
              fill=(120, 130, 150), outline=OUTL)
    d.line([(x - c(110), y - c(120)), (x + c(110), y - c(120))], fill=OUTL, width=6)
    d.ellipse([x - c(105), y - c(140), x + c(105), y - c(100)], fill=(225, 228, 238), outline=OUTL, width=5)
    d.arc([x - c(110), y - c(260), x + c(110), y - c(20)], 200, 340, fill=OUTL, width=7)

def bucket_props(frame, d, T, sc):
    lt = T - sc["s"]
    shake = 4 * math.sin(T * 30) if lt > 3 else 0
    bucket(d, 760 + shake, 1110, 1.1)
    if lt > 0.8:
        top_label(frame, "13.5x WATER", 380, YEL, 76)
    if lt > 3.0:
        l = label("135 KG", 64, YEL); comp(frame, l, 760 + shake - l.width / 2, 1080)

def jump_pos(T):
    lt = T - 18.0
    if lt < 1.2:
        p = lt / 1.2
        return (540, 560 + (SURF - 150 - 560) * p * p, 440)
    b = abs(math.sin((lt - 1.2) * 5)) * 60 * math.exp(-(lt - 1.2) * 1.6)
    return (540, SURF - 150 - b, 440)

def jump_after(frame, d, T, sc):
    surface_front(d, T)
    lt = T - sc["s"]
    if 1.1 < lt < 1.6:
        for k in range(10):
            a = math.pi * (k + 0.5) / 10; r = 60 + 300 * (lt - 1.1)
            x, y = 540 - math.cos(a) * r * 1.4, SURF - math.sin(a) * r * 0.6
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(225, 228, 238), outline=OUTL, width=3)
    if lt > 2.0:
        top_label(frame, "ONLY ~7% SINKS", 380, YEL, 76)

def swim_after(frame, d, T, sc):
    surface_front(d, T)
    lt = T - sc["s"]
    if lt > 1.0:
        top_label(frame, "13x HARDER", 380, YEL, 76)

def iron_ball(d, x, y, r):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(70, 72, 80), outline=OUTL, width=6)
    d.arc([x - r * 0.7, y - r * 0.8, x + r * 0.3, y], 200, 290, fill=(150, 150, 160), width=8)

def float_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = clamp(lt / 1.0)
    y = 700 + (SURF - 70 - 700) * p * p + (8 * math.sin(T * 3) if p >= 1 else 0)
    iron_ball(d, 360, y, 110)
    if lt > 1.5:
        l = label("IRON 7.9", 56, WHITE); comp(frame, l, 360 - l.width / 2, 960)
        l = label("MERCURY 13.5", 56, YEL); comp(frame, l, 540 - l.width / 2, 470)

def float_after(frame, d, T, sc):
    surface_front(d, T)

def payal(d, x, y, s=1.5):
    d.ellipse([x - 90 * s, y - 34 * s, x + 90 * s, y + 34 * s], outline=OUTL, width=int(20 * s))
    d.ellipse([x - 90 * s, y - 34 * s, x + 90 * s, y + 34 * s], outline=(214, 220, 230), width=int(12 * s))
    for k in range(9):
        a = math.pi * k / 8
        bx, by = x - 88 * s * math.cos(a), y + 34 * s * math.sin(a)
        d.ellipse([bx - 12 * s, by - 6 * s, bx + 12 * s, by + 18 * s], fill=(230, 234, 242), outline=OUTL, width=3)

def gold_coin(d, x, y, r=60):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 200, 50), outline=OUTL, width=6)
    d.ellipse([x - r * 0.65, y - r * 0.65, x + r * 0.65, y + r * 0.65], outline=(200, 140, 20), width=5)

def coin_y(lt):
    q = lt - 1.6
    return 760 + min(q, 0.8) ** 2 / 0.64 * (SURF - 760) + max(0, q - 0.8) * 60

def twist_after(frame, d, T, sc):
    lt = T - sc["s"]
    surface_front(d, T)
    p = clamp(lt / 0.8)
    payal(d, 250, 760 + (SURF - 20 - 760) * p * p + (6 * math.sin(T * 3) if p >= 1 else 0))
    if lt > 1.6:
        y = coin_y(lt)
        if y <= SURF:
            gold_coin(d, 830, y)
        else:
            a = 1 - 0.6 * clamp((lt - 2.6) / 3.5)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gold_coin(ImageDraw.Draw(layer), 830, y)
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
            frame.alpha_composite(layer)
    if lt > 1.0:
        l = label("SILVER 10.5", 56, WHITE); comp(frame, l, 250 - l.width / 2, 1110)
    if lt > 2.4:
        l = label("GOLD 19.3", 56, YEL); comp(frame, l, 830 - l.width / 2, 1110)

def thermometer(d, x, y):
    d.rounded_rectangle([x - 26, y - 260, x + 26, y + 160], radius=26, fill=WHITE, outline=OUTL, width=6)
    d.ellipse([x - 50, y + 120, x + 50, y + 220], fill=(200, 205, 215), outline=OUTL, width=6)
    d.rectangle([x - 10, y - 120, x + 10, y + 140], fill=(200, 205, 215))
    for k in range(6): d.line([(x + 6, y - 220 + k * 50), (x + 26, y - 220 + k * 50)], fill=OUTL, width=4)

def safety_props(frame, d, T, sc):
    lt = T - sc["s"]
    thermometer(d, 800, 1000)
    if lt > 0.8:
        r = 170
        d.ellipse([800 - r, 1030 - r, 800 + r, 1030 + r], outline=(230, 40, 50), width=22)
        d.line([(800 - r * 0.7, 1030 - r * 0.7), (800 + r * 0.7, 1030 + r * 0.7)], fill=(230, 40, 50), width=22)
    if lt > 0.6:
        top_label(frame, "DON'T TOUCH", 380, (255, 90, 90), 80)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="meet", s=4.0, e=11.0, bg_fn=mbg, clock="THE POOL", char="uncle", pos=(540, SURF - 200, 420),
         props=meet_props, look=(0, 0.4),
         narr="Mercury is the only METAL that stays LIQUID at room temperature.", n_at=4.2,
         say="Silver PAANI?!", say_at=7.4, pitch=150),
    dict(id="bucket", s=11.0, e=18.0, bg_fn=mbg, clock="ONE BUCKET", char="kid", state="puff",
         pos=(320, SURF - 190, 400), props=bucket_props, look=(0.6, 0.2),
         narr="It's 13.5 TIMES denser than water. A 10-litre bucket weighs about 135 KG!", n_at=11.2,
         say="It won't BUDGE!", say_at=14.6, pitch=400),
    dict(id="jump", s=18.0, e=25.0, bg_fn=mbg, clock="JUMP IN", char="kid", pos=jump_pos,
         props_after=jump_after, look=(0, 0.3),
         narr="Jump in and you barely sink. Only about 7% of you goes UNDER.", n_at=18.4,
         say="I'm STANDING on it!", say_at=21.4, pitch=400),
    dict(id="swim", s=25.0, e=32.0, bg_fn=mbg, clock="TRY SWIMMING", char="kid", state="puff",
         pos=(540, SURF - 60, 440), rot=lambda T: -78 + 6 * math.sin(T * 8), props_after=swim_after,
         narr="Try to swim? Pushing your arm under is 13 TIMES harder than in water.", n_at=25.2,
         say="Best GYM ever!", say_at=28.8, pitch=400),
    dict(id="float", s=32.0, e=39.0, bg_fn=mbg, clock="DROP TEST", props=float_props, props_after=float_after,
         char="uncle", pos=(800, SURF - 170, 340), look=(-0.6, 0.2),
         narr="Even a heavy IRON ball would FLOAT on top, like a cork.", n_at=32.2,
         say="Iron... FLOATS?!", say_at=35.6, pitch=150),
    dict(id="twist", s=39.0, e=46.0, bg_fn=mbg, clock="PLOT TWIST", twist=True,
         props_after=twist_after, char="uncle", state="crown", pos=(540, 1010, 280), look=(0.5, 0.3),
         say="My GOLD!", say_at=43.0, pitch=150,
         narr="Twist: SILVER floats too. But GOLD sinks... and slowly DISSOLVES into it!", n_at=39.2),
    dict(id="safety", s=46.0, e=53.0, bg="living", clock="REAL LIFE", char="kid", pos=(330, 1080, 420),
         props=safety_props, look=(0.5, 0),
         narr="Real talk: mercury vapour is TOXIC. Never touch it, even from a broken thermometer.",
         n_at=46.2, say="Science from FAR away!", say_at=49.6, pitch=400),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = clamp((T - 1.9) / 0.5)
        r = 40 + 90 * ease_back(p)
        d.ellipse([540 - r * 1.6, 1420 - r * 0.5, 540 + r * 1.6, 1420 + r * 0.5], fill=(200, 205, 216),
                  outline=OUTL, width=6)
        d.line([(540 - r * 1.0, 1405), (540 - r * 0.2, 1400)], fill=WHITE, width=6)

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU JUMPED INTO", WHITE)], 120), 770, 0.75, "right"),
        (title([("A POOL OF ", WHITE), ("MERCURY?", YEL)], 120), 910, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 100), 470, 0.15),
                      (title([("drop in first?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("kid", "puff"), ("uncle", "hat"), ("cat", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=38.85), dict(t0=46.0, t1=53.0, drums=False),
           dict(t0=53.0, t1=58.0, melody=True)],
    fx=[("splash", 19.2, 0.6), ("pop", 19.4, 0.5), ("pop", 34.0, 0.4), ("pop", 39.8, 0.4),
        ("bubbles", 41.0, 0.4, dict(dd=3.0)), ("ding", 43.6, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_jumped_into_a_pool_of_mercury")
