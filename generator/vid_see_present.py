#!/usr/bin/env python3
"""What if you could see the present? Facts: light travels ~299,792 km/s, so 30 cm takes ~1 nanosecond (0.3 / 3e8 s).
Perception lags by at least 80 ms (Salk Institute, Eagleman & Sejnowski, Science 2000); information takes several
dozen ms to reach the brain and the brain extrapolates moving objects forward to predict the present (The Conversation /
University of Melbourne, PNAS study). Moon ~384,400 km -> ~1.3 s. Sun ~149.6 million km -> ~499 s = 8 min 20 s.
Earth-Mars one-way signal delay 3-22 minutes (NASA Perseverance blog). Polaris (Dhruva in the Puranas) ~446 ly
(Gaia DR3; estimates range ~320-520 ly) -> light left in the Mughal era (1526-1857). Andromeda M31 is 2.5 million ly
away and visible to the unaided eye from a dark site (NASA Hubble Messier catalogue); Homo sapiens ~300,000 years old.
Twist: a mirror 1 m away = 2 m light path = ~6.7 ns."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 60.0
BEAM = (255, 245, 170)
MARS = (214, 96, 60)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def put(frame, txt, cx, y, size=52, col=WHITE):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

_bgc = {}
def sky_bg():
    if "sky" not in _bgc:
        img = grad([(0, (8, 10, 34)), (0.7, (22, 26, 70)), (1, (40, 34, 80))], W, H)
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(11)
        for k in range(160):
            x = rng.uniform(0, W); y = rng.uniform(0, 1700); r = rng.uniform(1.2, 3.2)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 225, 255))
        d.rectangle([0, 1700, W, H], fill=(20, 22, 40))
        _bgc["sky"] = img
    return _bgc["sky"]

def beam(d, x0, y0, x1, y1, q, col=BEAM, w=10, dots=True):
    """Light pulse travelling from (x0,y0) to (x1,y1); q in 0..1."""
    xe, ye = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
    d.line([(x0, y0), (xe, ye)], fill=col, width=w)
    r = w * 1.6
    d.ellipse([xe - r, ye - r, xe + r, ye + r], fill=WHITE, outline=col, width=4)

def star(d, cx, cy, r, col=YEL, T=0.0):
    tw = 1 + 0.12 * math.sin(T * 6)
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r * tw if k % 2 == 0 else r * 0.42 * tw
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col, outline=OUTL, width=5)

def phone(d, cx, cy, s=1.0, T=0.0):
    w, h = 130 * s, 240 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=22 * s, fill=(40, 40, 52),
                        outline=OUTL, width=6)
    glow = int(190 + 40 * math.sin(T * 3))
    d.rounded_rectangle([cx - w / 2 + 12 * s, cy - h / 2 + 22 * s, cx + w / 2 - 12 * s, cy + h / 2 - 22 * s],
                        radius=10 * s, fill=(110, glow, 255))

# ---------------------------------------------------------------- props
def phone_props(frame, d, T, sc):
    lt = T - sc["s"]
    phone(d, 800, 1020, 1.2, T)
    q = ((lt - 0.8) % 1.2) / 1.2 if lt > 0.8 else 0
    if lt > 0.8: beam(d, 720, 1000, 400, 960, q)
    if lt > 0.5: top_label(frame, "30 CM AWAY", 380, YEL, 96)
    if lt > 2.5: put(frame, "= 1 NANOSECOND", 540, 500, 70, WHITE)

def brain(d, cx, cy, r, T):
    pink = (246, 160, 186)
    for k, (dx, dy, rr) in enumerate([(-0.45, -0.1, 0.6), (0.45, -0.1, 0.6), (-0.1, -0.4, 0.55), (0.2, 0.25, 0.55),
                                      (-0.35, 0.3, 0.5)]):
        x, y, q = cx + dx * r, cy + dy * r, rr * r * (1 + 0.03 * math.sin(T * 4 + k))
        d.ellipse([x - q, y - q * 0.8, x + q, y + q * 0.8], fill=pink, outline=OUTL, width=6)
    for k in range(4):
        x = cx - r * 0.6 + k * r * 0.4
        d.arc([x - 40, cy - 50, x + 40, cy + 30], 200, 340, fill=(200, 100, 130), width=6)

def brain_props(frame, d, T, sc):
    lt = T - sc["s"]
    brain(d, 540, 760, 170, T)
    # a ball and the brain's guess drawn ahead of it
    x = 120 + ((lt * 260) % 820)
    y = 1180
    d.ellipse([x + 120 - 46, y - 46, x + 120 + 46, y + 46], fill=None, outline=YEL, width=6)
    d.ellipse([x - 40, y - 40, x + 40, y + 40], fill=(214, 60, 60), outline=OUTL, width=6)
    if lt > 1.5: put(frame, "GUESS", min(x + 120, 960), 1250, 46, YEL)
    if lt > 0.5: top_label(frame, "80 MILLISECONDS", 380, YEL, 92)

def moon_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    mini(frame, "moon", 760, 820, 340 * p, T)
    mini(frame, "earth", 220, 1180, 200, T, state=T * 0.2)
    q = ((lt - 0.8) % 1.3) / 1.3 if lt > 0.8 else 0
    if lt > 0.8: beam(d, 690, 900, 290, 1120, q)
    if lt > 0.5: top_label(frame, "1.3 SECONDS OLD", 380, YEL, 92)

def sun_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    mini(frame, "sun", 760, 800, 380 * p, T)
    mini(frame, "earth", 200, 1200, 150, T, state=T * 0.2)
    if lt > 0.5: top_label(frame, "8 MIN 20 SEC OLD", 380, YEL, 92)

def mars_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "earth", 180, 1150, 200, T, state=T * 0.2)
    r = 130
    d.ellipse([830 - r, 820 - r, 830 + r, 820 + r], fill=MARS, outline=OUTL, width=7)
    for (dx, dy, rr) in [(-40, -30, 26), (40, 40, 20), (10, -70, 14)]:
        d.ellipse([830 + dx - rr, 820 + dy - rr, 830 + dx + rr, 820 + dy + rr], fill=(170, 70, 44))
    # a slow signal: dashes crawling
    q = clamp((lt - 0.8) / 5.5)
    if lt > 0.8: beam(d, 270, 1090, 720, 880, q, col=(140, 230, 255), w=8)
    if lt > 0.5: top_label(frame, "3 TO 22 MINUTES", 380, YEL, 92)

def dhruv_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    star(d, 540, 760, 120 * p, YEL, T)
    if lt > 0.5: top_label(frame, "DHRUV TARA", 380, YEL, 110)
    if lt > 2.0: put(frame, "~450 YEARS AGO", 540, 960, 70, WHITE)

def galaxy(frame, cx, cy, s, T):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    for k in range(9, 0, -1):
        a = 30 + k * 22
        d.ellipse([cx - s * k / 9, cy - s * 0.35 * k / 9, cx + s * k / 9, cy + s * 0.35 * k / 9],
                  fill=(200, 190, 255, a))
    d.ellipse([cx - s * 0.18, cy - s * 0.1, cx + s * 0.18, cy + s * 0.1], fill=(255, 250, 220, 255))
    L = L.rotate(-25 + 3 * math.sin(T * 0.5), center=(cx, cy), resample=Image.BICUBIC)
    frame.alpha_composite(L)

def andro_props(frame, d, T, sc):
    lt = T - sc["s"]
    galaxy(frame, 540, 820, 380 * ease_out(clamp(lt / 1.0)), T)
    if lt > 0.5: top_label(frame, "ANDROMEDA", 380, YEL, 110)
    if lt > 2.0: put(frame, "2.5 MILLION YEARS OLD", 540, 1050, 64, WHITE)

def mirror_props(frame, d, T, sc):
    lt = T - sc["s"]
    # mirror on the right
    d.rounded_rectangle([640, 600, 960, 1340], radius=150, fill=(170, 120, 70), outline=OUTL, width=8)
    d.rounded_rectangle([668, 628, 932, 1312], radius=130, fill=(200, 230, 250))
    mini(frame, "kid", 800, 1030, 300, T, look=(-0.6, -0.1))
    if lt > 0.5: top_label(frame, "MIRROR, 1 M AWAY", 380, YEL, 90)

# ---------------------------------------------------------------- scenes
S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="phone", s=4.0, e=11.0, bg="bedroom", clock="RIGHT NOW", props=phone_props, char="kid",
         pos=(300, 1060, 380), look=(0.7, -0.1),
         narr="Your phone is 30 CM away. Its light takes about 1 BILLIONTH of a second to reach you.",
         n_at=4.2, narr_y=1580),
    dict(id="brain", s=11.0, e=18.0, bg="living", clock="+ BRAIN", props=brain_props,
         narr="Then your BRAIN needs at least 80 MILLISECONDS to make sense of it, so it GUESSES ahead.",
         n_at=11.2, narr_y=1580),
    dict(id="moon", s=18.0, e=25.0, bg_fn=lambda T: sky_bg(), clock="TONIGHT", props=moon_props,
         narr="Look up. The MOON you see is about 1.3 SECONDS old.", n_at=18.2, narr_y=1580),
    dict(id="sun", s=25.0, e=32.0, bg="space", clock="SUNLIGHT", props=sun_props,
         narr="The SUN is 8 MINUTES 20 SECONDS old. And never stare at it directly!", n_at=25.2,
         narr_y=1580),
    dict(id="mars", s=32.0, e=39.0, bg="space", clock="HELLO MARS", props=mars_props,
         narr="A signal to MARS takes 3 to 22 MINUTES, so rovers can't be driven live.", n_at=32.2,
         narr_y=1580),
    dict(id="dhruv", s=39.0, e=46.0, bg_fn=lambda T: sky_bg(), clock="POLE STAR", props=dhruv_props,
         narr="DHRUV TARA's light left it about 450 YEARS ago, back in the MUGHAL era.", n_at=39.2,
         narr_y=1580),
    dict(id="andro", s=46.0, e=53.0, bg_fn=lambda T: sky_bg(), clock="DARK SKY", props=andro_props,
         narr="ANDROMEDA, visible from a dark sky, sends light older than HUMANS themselves.", n_at=46.2,
         narr_y=1580),
    dict(id="never", s=53.0, e=TW, bg_fn=lambda T: sky_bg(), clock="SO...", char="kid", pos=(540, 1060, 520),
         look=(0, -0.6),
         narr="So you can NEVER see the present. Everything you see is a message from the PAST.", n_at=53.2,
         narr_y=1580, say="Wait... WHAT?", say_at=56.0, pitch=440),
    dict(id="twist", s=TW, e=67.0, bg="bedroom", clock="PLOT TWIST", props=mirror_props,
         char="kid", pos=(300, 1060, 380), look=(0.7, -0.1), twist=True,
         narr="Twist: your MIRROR always shows a YOU about 7 BILLIONTHS of a second younger!",
         n_at=TW + 0.2, narr_y=1600, say="Forever YOUNG!", say_at=TW + 3.6, pitch=440),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        star(d, 540, 1260, 130 * p, YEL, T)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU COULD SEE", WHITE)], 120), 730, 0.75, "right"),
        (title([("THE PRESENT?", YEL)], 140), 880, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which old light will ", WHITE), ("YOU", YEL)], 84), 470, 0.15),
                      (title([("look at tonight?", YEL)], 90), 600, 0.45)],
               row=[("kid", 1), ("moon", 1), ("sun", 1), ("earth", 1), ("rocket", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=46.0, dur=7.0, g=0.1)],
    fx=[("click", 5.0, 0.3), ("whoosh", 12.0, 0.3), ("ding", 19.5, 0.15), ("whoosh", 33.0, 0.3),
        ("ding", 41.0, 0.15), ("ding", 48.0, 0.15), ("pop", 63.6, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_could_see_the_present")
