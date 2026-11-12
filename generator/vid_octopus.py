#!/usr/bin/env python3
"""What if you were an octopus for a day? Facts: octopuses have eight arms (no tentacles), suckers along their length
and a hard, sharp beak; with no skeleton they can squeeze through tiny openings (EarthDate 'Amazing Octopuses');
"any space larger than their beak - one of the only hard parts of an octopus - is fair game" (Discover Magazine).
About two-thirds of an octopus's neurons are in its arms, and arms can work on tasks on their own (Smithsonian;
Harvard Gazette 2020; EarthDate). Suckers carry chemotactile receptors, so they taste by touch (Harvard Gazette 2020,
Cell). They change colour, shape and texture in under a tenth of a second using chromatophores and papillae; their
eyes have only one type of photoreceptor, and opsins in the skin respond to light (EarthDate). Three hearts: two pump
blood past the gills, one pumps it to organs and muscles; blood uses copper-based hemocyanin, so it looks blue
(Smithsonian). Ink hides the animal and contains tyrosinase, which irritates a predator's eyes and garbles smell and
taste (Smithsonian). Twist: the systemic heart stops beating when the octopus swims, which explains why they prefer
crawling (Smithsonian)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 60.0
OCT = (236, 110, 120)
OCT_D = (196, 74, 92)

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

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2)):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, 0, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def mix(a, b, t):
    return tuple(int(x * (1 - t) + y * t) for x, y in zip(a, b))

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def reef_bg():
    if "reef" not in _bgc:
        img = grad([(0, (50, 150, 200)), (0.6, (24, 90, 150)), (1, (14, 52, 96))], W, H)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1330, W, H], fill=(214, 190, 140))
        rng = np.random.default_rng(3)
        for k in range(10):
            x = rng.uniform(0, W); r = rng.uniform(40, 100)
            d.ellipse([x - r, 1320 - r * 0.45, x + r, 1320 + r * 0.45], fill=(196, 170, 120))
        for k in range(36):
            x = rng.uniform(0, W); y = rng.uniform(0, 1250); r = rng.uniform(2, 5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(160, 210, 240))
        _bgc["reef"] = img
    return _bgc["reef"]

SAND = (214, 190, 140)

# ---------------------------------------------------------------- octopus
def octopus(frame, cx, cy, s, T, col=OCT, face=True, squeeze=0.0, wave=1.0, arms_up=0.0, look=(0, 0.2),
            alpha=255):
    """Mantle centred at (cx, cy); s ~ mantle half-width."""
    if s < 3: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    dark = tuple(max(0, c - 40) for c in col)
    ow = max(2, int(s / 22))
    mw = s * (1 - 0.55 * squeeze); mh = s * 1.15 * (1 + 0.3 * squeeze)
    base_y = cy + mh * 0.55
    # arms
    for k in range(8):
        side = -1 if k < 4 else 1
        j = k % 4
        a0 = math.radians(side * (12 + j * 22))
        pts = []
        ln = s * (2.1 - 0.5 * squeeze)
        for i in range(14):
            t = i / 13
            ang = a0 + side * t * (0.9 - 1.6 * arms_up) + wave * 0.35 * math.sin(T * 3 + k * 0.9 + t * 4)
            x = cx + side * mw * 0.25 * (j / 3) + math.sin(ang) * ln * t
            y = base_y + math.cos(ang) * ln * t * (1 - 1.7 * arms_up)
            pts.append((x, y))
        for extra, c in ((2 * ow, OUTL), (0, col)):
            for i in range(13):
                wdt = s * 0.34 * (1 - 0.75 * i / 13) * (1 - 0.4 * squeeze) + extra
                d.line([pts[i], pts[i + 1]], fill=c, width=max(2, int(wdt)))
                r = wdt / 2
                x, y = pts[i + 1]
                d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        # suckers
        if s > 60:
            for i in range(3, 13, 3):
                x, y = pts[i]
                r = s * 0.05 * (1 - i / 16)
                d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 214, 200), outline=dark)
    # mantle
    d.ellipse([cx - mw, cy - mh, cx + mw, cy + mh * 0.75], fill=col, outline=OUTL, width=ow)
    d.ellipse([cx - mw * 0.5, cy - mh * 0.8, cx - mw * 0.15, cy - mh * 0.5], fill=mix(col, WHITE, 0.35))
    if face and s > 30:
        for ex in (-0.38, 0.38):
            x = cx + ex * mw * 1.25; y = cy + mh * 0.25; r = s * 0.2
            d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE, outline=OUTL, width=max(2, ow - 1))
            pr = r * 0.5
            px = x + look[0] * r * 0.4; py = y + look[1] * r * 0.4
            d.rectangle([px - pr, py - pr * 0.45, px + pr, py + pr * 0.45], fill=OUTL)
        d.arc([cx - s * 0.2, cy + mh * 0.35, cx + s * 0.2, cy + mh * 0.62], 20, 160, fill=OUTL,
              width=max(2, ow - 1))
    if alpha < 255:
        a = L.split()[3].point(lambda v: v * alpha // 255)
        L.putalpha(a)
    frame.alpha_composite(L)

def ink_cloud(d, cx, cy, r, T):
    rng = np.random.default_rng(9)
    for k in range(14):
        a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0.2, 1.0) * r
        x = cx + math.cos(a) * rr; y = cy + math.sin(a) * rr * 0.8
        q = rng.uniform(0.35, 0.6) * r
        d.ellipse([x - q, y - q, x + q, y + q], fill=(30, 26, 46))

def heart_shape(d, cx, cy, s, col, beat):
    s = s * (1 + 0.12 * beat)
    d.ellipse([cx - s, cy - s * 0.8, cx, cy + s * 0.2], fill=col, outline=OUTL, width=5)
    d.ellipse([cx, cy - s * 0.8, cx + s, cy + s * 0.2], fill=col, outline=OUTL, width=5)
    d.polygon([(cx - s * 0.97, cy - s * 0.15), (cx + s * 0.97, cy - s * 0.15), (cx, cy + s * 1.05)], fill=col)
    d.line([(cx - s * 0.97, cy - s * 0.15), (cx, cy + s * 1.05), (cx + s * 0.97, cy - s * 0.15)], fill=OUTL, width=5)

# ---------------------------------------------------------------- props
def wake_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    octopus(frame, 600, 900, 170 * p, T, look=(-0.6, 0.1))
    if lt > 0.5: top_label(frame, "8 ARMS. 0 BONES.", 380, YEL, 92)
    if lt > 2.0:
        put(frame, "+ 1 HARD BEAK", 540, 500, 64, WHITE)

def squeeze_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a rock wall with a small gap at y 950-1050 x 520-560
    d.rectangle([470, 560, 610, 1330], fill=(120, 112, 128), outline=OUTL, width=6)
    d.rectangle([462, 960, 618, 1040], fill=(36, 96, 150))
    q = clamp((lt - 0.8) / 4.2)
    x = 230 + 640 * q
    sq = max(0.0, 1 - abs(x - 540) / 160)
    octopus(frame, x, 990 - 160 * (1 - sq) * 0, 110, T, squeeze=0.8 * sq, wave=0.6, look=(1, 0))
    d.rectangle([470, 560, 610, 958], fill=(120, 112, 128), outline=OUTL, width=6)
    d.rectangle([470, 1042, 610, 1330], fill=(120, 112, 128), outline=OUTL, width=6)
    if lt > 0.5: top_label(frame, "ANY GAP > YOUR BEAK", 380, YEL, 84)

def arms_props(frame, d, T, sc):
    lt = T - sc["s"]
    octopus(frame, 540, 860, 150, T, look=(0, 0.3))
    tasks = [("OPEN SHELL", 190, 1250), ("EXPLORE", 890, 1250), ("HIDE", 220, 640), ("HUNT", 860, 640)]
    for k, (t, x, y) in enumerate(tasks):
        if lt > 1.0 + k * 0.9:
            put(frame, t, x, y, 50, WHITE)
    if lt > 0.5: top_label(frame, "2/3 OF NEURONS = ARMS", 380, YEL, 80)

def taste_props(frame, d, T, sc):
    lt = T - sc["s"]
    octopus(frame, 420, 880, 150, T, look=(1, 0.3))
    # a crab-like snack
    cx, cy = 820, 1260
    d.ellipse([cx - 70, cy - 45, cx + 70, cy + 45], fill=(230, 120, 50), outline=OUTL, width=5)
    for s_ in (-1, 1):
        for k in range(3):
            d.line([(cx + s_ * 50, cy + 10 + k * 10), (cx + s_ * 100, cy + 40 + k * 12)], fill=OUTL, width=6)
    for ex in (-22, 22):
        d.ellipse([cx + ex - 9, cy - 70, cx + ex + 9, cy - 52], fill=WHITE, outline=OUTL, width=3)
    if lt > 2.2:
        put(frame, "YUM?", 820, 1080, 64, YEL)
    if lt > 0.5: top_label(frame, "SUCKERS THAT TASTE", 380, YEL, 86)

def camo_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 1.5) / 0.4)
    q2 = clamp((lt - 4.0) / 0.4)
    col = mix(OCT, SAND, q)
    col = mix(col, (180, 80, 160), q2 * (0.5 + 0.5 * math.sin(T * 8) ** 2))
    octopus(frame, 540, 1130, 150, T, col=col, wave=0.4, look=(0, 0.3), alpha=int(255 - 120 * q * (1 - q2)))
    if lt > 1.0: put(frame, "0.1 SECONDS", 540, 560, 80, WHITE)
    if lt > 0.5: top_label(frame, "NOW YOU SEE ME...", 380, YEL, 86)

def eye_props(frame, d, T, sc):
    lt = T - sc["s"]
    # one big eye with a single "sensor" label
    cx, cy = 540, 900
    d.ellipse([cx - 230, cy - 170, cx + 230, cy + 170], fill=WHITE, outline=OUTL, width=8)
    d.rectangle([cx - 120, cy - 45, cx + 120, cy + 45], fill=OUTL)
    if lt > 1.2: put(frame, "1 TYPE OF COLOUR SENSOR", 540, 1120, 58, WHITE)
    if lt > 3.2: put(frame, "SKIN SENSES LIGHT TOO", 540, 1210, 58, YEL)
    if lt > 0.5: top_label(frame, "COLOUR-BLIND EYES?", 380, YEL, 86)

def hearts_props(frame, d, T, sc):
    lt = T - sc["s"]
    beat = max(0.0, math.sin(T * 7)) ** 3
    blue = (70, 110, 230)
    for k, (x, s, t) in enumerate([(260, 80, "GILLS"), (820, 80, "GILLS"), (540, 120, "BODY")]):
        if lt > 0.8 + k * 0.6:
            heart_shape(d, x, 830 if k < 2 else 760, s, blue, beat)
            put(frame, t, x, 950 if k < 2 else 920, 54, WHITE)
    if lt > 3.0:
        put(frame, "COPPER = BLUE BLOOD", 540, 1120, 66, YEL)
    if lt > 0.5: top_label(frame, "3 HEARTS!", 380, YEL, 120)

def ink_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 2.0) / 1.0)
    ox = 520 + 300 * ease_out(clamp((lt - 1.9) / 1.0))
    octopus(frame, ox, 860, 110, T, look=(1, 0))
    mini(frame, "fish", 230 + 60 * clamp(lt / 2), 1000, 320, T, look=(1, 0))
    if q > 0:
        ink_cloud(d, 470, 920, 230 * ease_out(q), T)
    if lt > 3.4: put(frame, "STINGS EYES + NOSE", 540, 1260, 60, WHITE)
    if lt > 0.5: top_label(frame, "INK ESCAPE", 380, YEL, 110)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    swim = lt < 3.4
    if swim:
        q = clamp(lt / 3.4)
        octopus(frame, 640, 1010 - 120 * math.sin(q * math.pi), 120, T, arms_up=-0.25, wave=0.3, look=(0, -0.5))
        heart_shape(d, 170, 760, 60, (120, 140, 170), 0)
        put(frame, "MAIN HEART: PAUSED", 540, 520, 62, WHITE)
    else:
        q = clamp((lt - 3.4) / 3.0)
        octopus(frame, 420 + 300 * q, 1150, 120, T, wave=1.2, look=(1, 0.2))
        heart_shape(d, 170, 760, 60, (70, 110, 230), max(0.0, math.sin(T * 7)) ** 3)
        put(frame, "CRAWL MODE", 540, 520, 70, YEL)
    if lt > 0.3: top_label(frame, "WAIT, WHAT?", 380, YEL, 100)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wake", s=4.0, e=11.0, bg_fn=lambda T: reef_bg(), clock="6:00 AM", props=wake_props,
         narr="You wake up with 8 ARMS, NO BONES and a hard BEAK like a parrot's.", n_at=4.2, narr_y=1580),
    dict(id="squeeze", s=11.0, e=18.0, bg_fn=lambda T: reef_bg(), clock="8:00 AM", props=squeeze_props,
         narr="No skeleton, so you can squeeze through ANY gap bigger than your BEAK.", n_at=11.2,
         narr_y=1580),
    dict(id="arms", s=18.0, e=25.0, bg_fn=lambda T: reef_bg(), clock="10:00 AM", props=arms_props,
         narr="About TWO-THIRDS of your neurons sit in your ARMS. Each arm can work on its own.",
         n_at=18.2, narr_y=1580),
    dict(id="taste", s=25.0, e=32.0, bg_fn=lambda T: reef_bg(), clock="LUNCH", props=taste_props,
         narr="Your SUCKERS can TASTE what they touch. Every hug is also a snack check.", n_at=25.2,
         narr_y=1580),
    dict(id="camo", s=32.0, e=39.0, bg_fn=lambda T: reef_bg(), clock="2:00 PM", props=camo_props,
         narr="Change COLOUR, shape and texture in under a TENTH of a second.", n_at=32.2, narr_y=1580),
    dict(id="eye", s=39.0, e=46.0, bg_fn=lambda T: reef_bg(), clock="4:00 PM", props=eye_props,
         narr="Wild part: your eyes have only ONE type of light sensor. Your SKIN may help sense light.",
         n_at=39.2, narr_y=1580),
    dict(id="hearts", s=46.0, e=53.0, bg_fn=lambda T: reef_bg(), clock="6:00 PM", props=hearts_props,
         narr="THREE HEARTS: two for the gills, one for the body. And your blood is BLUE.", n_at=46.2,
         narr_y=1580),
    dict(id="ink", s=53.0, e=TW, bg_fn=lambda T: reef_bg(), clock="8:00 PM", props=ink_props,
         narr="Danger? Squirt INK that hides you and IRRITATES the attacker's eyes and smell.", n_at=53.2,
         narr_y=1580),
    dict(id="twist", s=TW, e=67.0, bg_fn=lambda T: reef_bg(), clock="PLOT TWIST", props=twist_props,
         twist=True,
         narr="Twist: your BODY HEART STOPS beating when you swim. That's why octopuses prefer to CRAWL!",
         n_at=TW + 0.2, narr_y=1600),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        octopus(frame, 540, 1200, 120 * p, T)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU WERE AN", WHITE)], 120), 690, 0.75, "right"),
        (title([("OCTOPUS?", YEL)], 170), 830, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("If ", WHITE), ("YOU", YEL), (" had 8 arms,", WHITE)], 96), 470, 0.15),
                      (title([("what would each one do?", YEL)], 80), 600, 0.45)],
               row=[("kid", 1), ("fish", 1), ("whale", 1), ("cat", 1), ("ladoo", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("bubbles", 4.3, 0.15, dict(dd=6.0)), ("pop", 13.5, 0.2), ("whoosh", 15.0, 0.3),
        ("pop", 19.0, 0.15), ("pop", 19.9, 0.15), ("pop", 20.8, 0.15), ("pop", 21.7, 0.15),
        ("ding", 27.4, 0.2), ("whoosh", 33.5, 0.3), ("whoosh", 36.0, 0.3),
        ("heartbeat", 47.0, 0.25, dict(dd=5.0, bpm=70)), ("splash", 55.0, 0.3),
        ("powerdown", TW + 0.6, 0.2), ("pop", TW + 3.5, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_were_an_octopus")
