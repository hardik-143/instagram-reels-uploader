#!/usr/bin/env python3
"""What if Betelgeuse exploded tonight? Red supergiant on Orion's shoulder (Ardra), ~750x the Sun's radius,
supernova as bright as a half Moon, visible by day for ~a year, harmless at 500+ light-years, probably ~100,000
years away, light left before the Taj Mahal. Twist: much of the iron in your body was forged in supernovae."""
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

RED = (236, 90, 60)

# ---------------------------------------------------------------- night sky with Orion
_sky = {}
def night_sky(seed=3):
    if seed in _sky: return _sky[seed]
    img = grad([(0, (6, 8, 30)), (0.7, (20, 22, 60)), (1, (34, 30, 74))], W, H)
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    for _ in range(260):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.85)
        r = rng.choice([1.2, 1.8, 2.5])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 220, 245))
    _sky[seed] = img
    return img

# Orion's main stars (x, y, radius); index 0 = Betelgeuse
ORION = [(400, 430, 22), (690, 460, 13), (480, 600, 10), (545, 590, 10), (610, 580, 10), (420, 760, 11), (700, 740, 14)]
ORION_LINES = [(0, 2), (1, 4), (2, 3), (3, 4), (2, 5), (4, 6), (0, 1)]

_gl = {}
def glow_spr(r, col, strength=0.8):
    k = (int(r), col, strength)
    if k not in _gl:
        R = int(r)
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        q = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / R, 0, 1) ** 2
        a = (q * 255 * strength).astype(np.uint8)
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = col[0], col[1], col[2], a
        _gl[k] = Image.fromarray(arr, "RGBA")
    return _gl[k]

def glow(ov, x, y, r, col, strength=0.8):
    g = glow_spr(r, col, strength)
    ov.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

def draw_orion(frame, T, beetle=True, scale=1.0, beetle_col=RED):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for a, b in ORION_LINES:
        if not beetle and 0 in (a, b): continue
        d.line([ORION[a][:2], ORION[b][:2]], fill=(140, 150, 220, 120), width=4)
    for i, (x, y, r) in enumerate(ORION):
        if i == 0:
            if not beetle: continue
            tw = 1 + 0.08 * math.sin(T * 5)
            glow(ov, x, y, r * scale * tw * 3.2, beetle_col)
            d.ellipse([x - r * scale, y - r * scale, x + r * scale, y + r * scale], fill=(255, 150, 110, 255))
        else:
            glow(ov, x, y, r * 2.0, (170, 200, 255), 0.6)
            d.ellipse([x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6], fill=(235, 240, 255, 255))
    frame.alpha_composite(ov)

def giant(d, cx, cy, r, T, face=True, worried=False):
    """Cartoon red supergiant with a face."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(226, 84, 54), outline=OUTL, width=6)
    for dx, dy, rr in ((-0.4, -0.35, 0.18), (0.35, 0.3, 0.22), (-0.2, 0.5, 0.12), (0.5, -0.4, 0.1)):
        d.ellipse([cx + (dx - rr) * r, cy + (dy - rr) * r, cx + (dx + rr) * r, cy + (dy + rr) * r], fill=(240, 120, 70))
    if face:
        e = 0.1 * r
        for ex in (cx - 0.28 * r, cx + 0.28 * r):
            d.ellipse([ex - e, cy - 0.15 * r - e * 1.2, ex + e, cy - 0.15 * r + e * 1.2], fill=WHITE, outline=OUTL, width=4)
            d.ellipse([ex - e * 0.5, cy - 0.12 * r - e * 0.5, ex + e * 0.5, cy - 0.12 * r + e * 0.5], fill=(25, 20, 30))
        if worried:
            d.ellipse([cx - 0.1 * r, cy + 0.15 * r, cx + 0.1 * r, cy + 0.35 * r], fill=(80, 20, 20), outline=OUTL, width=4)
        else:
            d.arc([cx - 0.25 * r, cy + 0.0 * r, cx + 0.25 * r, cy + 0.3 * r], 20, 160, fill=OUTL, width=6)

def burst(frame, cx, cy, r, T, a=255):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if a > 0: glow(ov, cx, cy, r * 4, (255, 240, 200), 0.9 * a / 255)
    n = 12
    for k in range(n):
        ang = k * 2 * math.pi / n + T * 0.4
        L = r * (2.6 if k % 2 else 1.8)
        p1 = (cx + math.cos(ang) * L, cy + math.sin(ang) * L)
        p2 = (cx + math.cos(ang + 0.12) * r * 0.5, cy + math.sin(ang + 0.12) * r * 0.5)
        p3 = (cx + math.cos(ang - 0.12) * r * 0.5, cy + math.sin(ang - 0.12) * r * 0.5)
        d.polygon([p1, p2, p3], fill=(255, 250, 220, a))
    d.ellipse([cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6], fill=(255, 255, 245, a))
    frame.alpha_composite(ov)

# ---------------------------------------------------------------- scenes
def meet_props(frame, d, T, sc):
    draw_orion(frame, T)
    lt = T - sc["s"]
    if lt > 1.0:
        l = label("ARDRA", 50, YEL)
        comp(frame, l, 250 - l.width / 2, 490)

def size_bg(T):
    return E.bg("space")

ORB = [(90, (180, 170, 160)), (140, (236, 200, 120)), (200, (80, 150, 230)), (270, (210, 100, 70))]
def size_props(frame, d, T, sc):
    cx, cy = 540, 900
    lt = T - sc["s"]
    for r, col in ORB:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 130, 190), width=3)
    for i, (r, col) in enumerate(ORB):
        a = T * (1.4 - i * 0.25) + i
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        pr = 14 if i != 2 else 20
        d.ellipse([x - pr, y - pr, x + pr, y + pr], fill=col, outline=OUTL, width=3)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 220, 90), outline=OUTL, width=3)
    if lt < 1.5:
        l = label("OUR SUN", 44, WHITE); comp(frame, l, cx - l.width / 2, cy + 300)

def size_after(frame, d, T, sc):
    lt = T - sc["s"]
    q = ease_out(clamp((lt - 1.6) / 2.4))
    if q > 0:
        giant(d, 540, 900, 20 + 300 * q, T, face=q > 0.6, worried=False)
    if lt > 4.2:
        l = label("~750 X THE SUN'S WIDTH", 54, YEL); comp(frame, l, 540 - l.width / 2, 360)

def flash(frame, T, sc):
    lt = T - sc["s"]
    if 0.9 <= lt < 1.6:
        a = 1 - (lt - 0.9) / 0.7
        frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 255, 240, 255)), 0.85 * a)
    return frame

def boom_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt < 1.0:
        draw_orion(frame, T, scale=1 + lt * 1.5)
    else:
        draw_orion(frame, T, beetle=False)
        r = 34 + 6 * math.sin(T * 6)
        burst(frame, ORION[0][0], ORION[0][1], r, T)
    if lt > 2.0:
        l = label("SUPERNOVA!", 66, YEL); comp(frame, l, 740 - l.width / 2, 340)

def day_props(frame, d, T, sc):
    burst(frame, 300, 520, 22 + 3 * math.sin(T * 6), T, a=230)

def danger_props(frame, d, T, sc):
    lt = T - sc["s"]
    burst(frame, 170, 560, 20, T, a=230)
    if lt > 1.0:
        x0, x1, y = 230, 820, 700
        d.line([(x0, y), (x1, y)], fill=WHITE, width=5)
        for x in (x0, x1):
            d.line([(x, y - 20), (x, y + 20)], fill=WHITE, width=5)
        l = label("500+ LIGHT-YEARS", 50, YEL); comp(frame, l, 525 - l.width / 2, y - 90)

def fade_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 0.5) / 3.0)
    if q < 1:
        a = int(230 * (1 - q))
        burst(frame, ORION[0][0], ORION[0][1], 26 * (1 - 0.6 * q), T, a=max(0, a))
    draw_orion(frame, T, beetle=False)
    if lt > 4.0:
        x, y = ORION[0][:2]
        d.ellipse([x - 40, y - 40, x + 40, y + 40], outline=YEL, width=5)
        l = label("?", 70, YEL); comp(frame, l, x - l.width / 2, y - 140)

def when_props(frame, d, T, sc):
    draw_orion(frame, T)
    lt = T - sc["s"]
    if lt > 1.2:
        l = label("~100,000 YEARS?", 60, YEL); comp(frame, l, 300 - l.width / 2, 980)

def taj(d, cx, by, s=1.0, col=(245, 240, 232)):
    """Simple Taj Mahal silhouette, base centre at (cx, by)."""
    S = lambda v: v * s
    d.rectangle([cx - S(230), by - S(30), cx + S(230), by], fill=col, outline=OUTL, width=4)
    d.rectangle([cx - S(130), by - S(190), cx + S(130), by - S(30)], fill=col, outline=OUTL, width=4)
    d.rounded_rectangle([cx - S(45), by - S(150), cx + S(45), by - S(30)], radius=S(45), fill=(200, 190, 180), outline=OUTL, width=3)
    d.ellipse([cx - S(95), by - S(330), cx + S(95), by - S(150)], fill=col, outline=OUTL, width=4)
    d.polygon([(cx - S(10), by - S(320)), (cx + S(10), by - S(320)), (cx, by - S(380))], fill=col, outline=OUTL)
    for mx in (-200, 200):
        d.rectangle([cx + S(mx) - S(14), by - S(260), cx + S(mx) + S(14), by - S(30)], fill=col, outline=OUTL, width=3)
        d.ellipse([cx + S(mx) - S(22), by - S(290), cx + S(mx) + S(22), by - S(250)], fill=col, outline=OUTL, width=3)

def light_props(frame, d, T, sc):
    lt = T - sc["s"]
    sx, sy = 200, 580
    giant(d, sx, sy, 60, T, face=False)
    tx, ty = 760, 1230
    # photons travelling down toward Earth
    for k in range(6):
        q = ((lt * 0.35 + k / 6) % 1.0)
        x = sx + (tx - sx) * q; y = sy + (ty - 160 - sy) * q
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 170, 120))
    taj(d, tx, ty, 0.8)
    if lt > 1.5:
        l = label("LEFT 500+ YEARS AGO", 54, YEL); comp(frame, l, 540 - l.width / 2, 360)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.2:
        l = label("IRON (FE): MADE IN STARS", 54, YEL); comp(frame, l, 540 - l.width / 2, 450)
    for k in range(10):
        a = k * 0.63 + T * 0.8
        r = 330 + 20 * math.sin(T * 2 + k)
        x, y = 540 + math.cos(a) * r, 1040 + math.sin(a) * r * 0.8
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(255, 230, 160))

def nbg(T): return night_sky()

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="meet", s=4.0, e=11.0, bg_fn=nbg, clock="ORION'S SHOULDER", char="kid", pos=(780, 1110, 320),
         props=meet_props, look=(-0.6, -0.6),
         narr="Betelgeuse is the red star on ORION's shoulder. In India, it's linked to ARDRA.", n_at=4.2,
         say="That RED dot?", say_at=7.6, pitch=620, bubble_y=870),
    dict(id="size", s=11.0, e=18.0, bg="space", clock="RED SUPERGIANT", props=size_props, props_after=size_after,
         narr="Put it where our Sun is, and it would swallow Mercury, Venus, EARTH and MARS.", n_at=11.2),
    dict(id="boom", s=18.0, e=25.0, bg_fn=nbg, clock="ONE NIGHT...", char="moon", pos=(760, 1070, 300),
         props=boom_props, overlay=flash, look=(-0.6, -0.5),
         narr="Now it EXPLODES. The supernova would shine about as bright as a HALF MOON.", n_at=19.4,
         say="Hey, that's MY job!", say_at=21.8, pitch=380, bubble_y=870),
    dict(id="day", s=25.0, e=32.0, bg="day", clock="VISIBLE BY DAY", char="kid", pos=(620, 1090, 400),
         props=day_props, look=(-0.6, -0.6),
         narr="You could spot it in DAYLIGHT for about a YEAR, then watch it fade for years.", n_at=25.2,
         say="Two SUNS today?", say_at=28.4, pitch=620, bubble_y=870),
    dict(id="danger", s=32.0, e=39.0, bg="space", clock="ARE WE SAFE?", char="earth", pos=(780, 1060, 330),
         props=danger_props, state=lambda T: T * 12, look=(-0.6, -0.3),
         narr="Danger to Earth? NO. It's over 500 LIGHT-YEARS away, far outside the danger zone.", n_at=32.2,
         say="PHEW!", say_at=35.4, pitch=300, bubble_y=870),
    dict(id="fade", s=39.0, e=46.0, bg_fn=nbg, clock="YEARS LATER", char="kid", state="puff", pos=(780, 1110, 320),
         props=fade_props, look=(-0.6, -0.6),
         narr="When the glow finally fades, Orion would lose its SHOULDER for good.", n_at=39.2,
         say="Orion needs a PHYSIO!", say_at=42.6, pitch=620, bubble_y=870),
    dict(id="when", s=46.0, e=53.0, bg_fn=nbg, clock="SO... WHEN?", char="uncle", state="hat", pos=(780, 1110, 340),
         props=when_props, look=(-0.6, -0.5),
         narr="Don't stay up. A 2020 study says it's probably about 100,000 YEARS away.", n_at=46.2,
         say="Wake me UP then.", say_at=49.4, pitch=200, bubble_y=800),
    dict(id="light", s=53.0, e=60.0, bg_fn=nbg, clock="OLD LIGHT", props=light_props,
         narr="And its light takes over 500 YEARS to reach us. It left before the TAJ MAHAL was built.", n_at=53.2),
    dict(id="twist", s=60.0, e=67.0, bg="twist", clock="PLOT TWIST", char="heart", pos=(540, 1040, 420),
         props=twist_props, twist=True,
         narr="Twist: much of the IRON in your body was forged in exploding stars like this.", n_at=60.2,
         say="I'm made of STARS!", say_at=63.4, pitch=260, bubble_y=760),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        giant(d, 540, 1450, 150 * p, T, face=p > 0.6, worried=True)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("BETELGEUSE", WHITE)], 130), 720, 0.75, "right"),
        (title([("EXPLODED", WHITE)], 140), 865, 1.05, "left"),
        (title([("TONIGHT?", YEL)], 130), 1015, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" stay up", WHITE)], 100), 470, 0.15),
                      (title([("to watch it?", YEL)], 116), 600, 0.45)],
               row=[("kid", 1), ("moon", 1), ("earth", 1), ("heart", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=25.0, drums=False, minor=True), dict(t0=25.0, t1=59.85, melody=True),
           dict(t0=67.0, t1=72.0, melody=True)],
    drones=[dict(t0=60.2, dur=6.5, g=0.05)],
    fx=[("rumble", 12.6, 0.5, dict(dd=3.0)), ("boom", 18.9, 0.8), ("crash", 19.0, 0.3), ("gasp", 22.0, 0.4),
        ("pop", 28.0, 0.4), ("powerdown", 39.6, 0.4), ("ding", 53.8, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_betelgeuse_exploded_tonight")
