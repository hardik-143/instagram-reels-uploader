#!/usr/bin/env python3
"""What if you could regrow like a planarian? Facts: planarians are freshwater flatworms that can regenerate a whole
animal from small pieces (Wikipedia: Neoblast; biovoicenews/inStem). T.H. Morgan (1898, 'Experimental studies of the
regeneration of Planaria maculata', The Node) found a piece 1/279th of a worm could regrow a new worm, taking one to
two weeks (Wikipedia: Neoblast). Neoblasts (adult pluripotent stem cells) make up to 30% of all cells (Wikipedia).
Wagner, Wang & Reddien 2011 (Science; Whitehead Institute news): one transplanted neoblast in an irradiated worm with
no stem cells multiplied and replaced all the host's tissues. Shomrat & Levin 2013 (Tufts Now): worms trained to feed
in a lit area, decapitated, regrew heads in ~2 weeks and after a refresher were significantly quicker to feed there.
Human liver: up to 70% can be removed for living donation and it regrows to nearly full size in about 3-4 weeks
(Mayo Clinic News Network). inStem (Institute for Stem Cell Science and Regenerative Medicine) with NCBS, Bengaluru,
study planarian regeneration (biovoicenews; instem.res.in). Twist: 15 D. japonica flatworms launched 10 Jan 2015 on
SpaceX-5, ~5 weeks on the ISS; one cut worm regenerated with two heads; cut again on Earth, the middle fragment
regrew two heads (ISS National Lab; Tufts / Levin, published 2017)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 60.0
BODY = (150, 98, 62)
BODY_D = (110, 70, 44)
PALE = (246, 236, 222)
GLOW = (120, 255, 200)

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

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def pond_bg():
    if "pond" not in _bgc:
        img = grad([(0, (90, 170, 160)), (0.55, (50, 120, 120)), (1, (30, 80, 84))], W, H)
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(4)
        for k in range(14):
            x = rng.uniform(0, W); y = rng.uniform(1300, 1900); r = rng.uniform(40, 110)
            d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(70, 100, 96))
        for k in range(30):
            x = rng.uniform(0, W); y = rng.uniform(0, 1250); r = rng.uniform(3, 9)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(160, 220, 210), width=2)
        _bgc["pond"] = img
    return _bgc["pond"]

def lab_bg():
    if "lab" not in _bgc:
        img = grad([(0, (226, 236, 246)), (1, (196, 210, 228))], W, H)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1320, W, H], fill=(150, 160, 176))
        d.rectangle([0, 1310, W, 1330], fill=(110, 118, 134))
        for x in (90, 950):
            d.rounded_rectangle([x - 40, 1180, x + 40, 1312], radius=14, fill=(200, 240, 255), outline=OUTL, width=5)
            d.rectangle([x - 40, 1250, x + 40, 1312], fill=(110, 200, 170))
        _bgc["lab"] = img
    return _bgc["lab"]

# ---------------------------------------------------------------- planarian
_TAIL_E = [0, 0.1, 0.3, 1]; _TAIL_H = [0.06, 0.5, 0.95, 1]
_HEAD_E = [0, 0.03, 0.1, 0.13, 0.2, 0.35, 1]; _HEAD_H = [0.12, 0.6, 1.08, 1.0, 0.72, 1.0, 1.0]

def worm_profile(s, left, right):
    """Half-width (0..1) at s in [0,1]; left/right = 'head' or 'tail'."""
    def end(e, kind):
        return np.interp(e, _HEAD_E, _HEAD_H) if kind == "head" else np.interp(e, _TAIL_E, _TAIL_H)
    return np.minimum(end(s, left), end(1 - s, right))

def worm_poly(cx, cy, L, Hh, T, s0, s1, left, right, wig=1.0, n=60):
    ss = np.linspace(s0, s1, n)
    hs = worm_profile(ss, left, right) * Hh
    xs = cx - L / 2 + ss * L
    ys = cy + wig * 12 * np.sin(ss * 2 * math.pi * 1.2 - T * 4)
    top = list(zip(xs, ys - hs)); bot = list(zip(xs, ys + hs))
    return top + bot[::-1], xs, ys

def planarian(frame, cx, cy, L, T, left="tail", right="head", body=(0.0, 1.0), grow=1.0, wig=1.0, dots=None):
    """Draws a flatworm facing right. body=(a,b): pigmented part in s; the rest is pale regrowing tissue whose
    extent scales with grow (0..1)."""
    d = ImageDraw.Draw(frame)
    Hh = L * 0.13
    a, b = body
    s0 = a - grow * a; s1 = b + grow * (1 - b)
    pts, _, _ = worm_poly(cx, cy, L, Hh, T, s0, s1, left, right, wig)
    d.polygon(pts, fill=PALE, outline=OUTL, width=max(3, int(L / 110)))
    pts2, xs, ys = worm_poly(cx, cy, L, Hh, T, a, b, left, right, wig)
    d.polygon(pts2, fill=BODY, outline=None)
    # mid stripe
    ss = np.linspace(a + 0.02, b - 0.02, 30)
    mx = cx - L / 2 + ss * L; my = cy + wig * 12 * np.sin(ss * 2 * math.pi * 1.2 - T * 4)
    if b - a > 0.08:
        d.line(list(zip(mx, my)), fill=BODY_D, width=max(3, int(Hh * 0.35)))
    d.polygon(pts, outline=OUTL, width=max(3, int(L / 110)))
    if dots is not None:
        dots(d, cx, cy, L, Hh, T, a, b)
    # eyes on each head end that has grown in
    for kind, e_s, side in ((left, s0, -1), (right, s1, 1)):
        if kind != "head": continue
        full = 1.0 if side == 1 else 0.0
        if abs(e_s - full) > 0.04: continue
        es = 1 - 0.11 if side == 1 else 0.11
        ex = cx - L / 2 + es * L
        ey = cy + wig * 12 * math.sin(es * 2 * math.pi * 1.2 - T * 4)
        r = Hh * 0.22
        for k in (-1, 1):
            yy = ey + k * Hh * 0.36
            d.ellipse([ex - r, yy - r, ex + r, yy + r], fill=WHITE, outline=OUTL, width=max(2, int(r / 4)))
            pr = r * 0.5
            py = yy - k * r * 0.45   # pupils point inwards: cross-eyed
            d.ellipse([ex - pr, py - pr, ex + pr, py + pr], fill=OUTL)

def blade(d, x, y0, y1, a=1.0):
    d.polygon([(x - 18, y0), (x + 18, y0), (x + 6, y1), (x - 6, y1)], fill=(220, 226, 236), outline=OUTL)

# ---------------------------------------------------------------- props
def meet_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    planarian(frame, 540 + 30 * math.sin(T * 0.8), 1000, 760 * p + 2, T)
    if lt > 0.5: top_label(frame, "THE PLANARIAN", 380, YEL, 96)
    if lt > 1.2: put(frame, "a freshwater flatworm", 540, 500, 56, WHITE)

def cut_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt < 1.4:
        planarian(frame, 540, 1000, 760, T)
        if lt > 0.8: blade(d, 540, 700 + 200 * clamp((lt - 0.8) / 0.4), 1150)
        top_label(frame, "1 WORM", 380, YEL, 100)
    else:
        sep = 160 * ease_out(clamp((lt - 1.4) / 0.6))
        g = clamp((lt - 2.2) / 3.8)
        # left half: tail piece regrows head; right half: head piece regrows tail
        planarian(frame, 400 - sep * 0.6, 940, 520, T, body=(0.0, 0.5), grow=g)
        planarian(frame, 680 + sep * 0.6, 1180, 520, T, body=(0.5, 1.0), grow=g)
        top_label(frame, "2 WORMS!" if g > 0.95 else "REGROWING...", 380, YEL, 100)

def morgan_props(frame, d, T, sc):
    lt = T - sc["s"]
    put(frame, "1/279", 540, 560, 150, YEL)
    g = clamp((lt - 1.2) / 4.5)
    L = 700
    piece = (0.5, 0.5 + 1 / 60)   # drawn a bit bigger than 1/279 so it's visible
    planarian(frame, 540, 1020, L, T, body=piece, grow=g, wig=0.4)
    if g < 0.1:
        put(frame, "tiny piece", 540, 1100, 52, WHITE)
    if lt > 0.5: top_label(frame, "1898", 380, YEL, 96)

def neo_dots(n_max, phase_fn=None):
    rng = np.random.default_rng(7)
    pts = [(rng.uniform(0.12, 0.88), rng.uniform(-0.6, 0.6)) for _ in range(200)]
    def f(d, cx, cy, L, Hh, T, a, b):
        n = n_max(T) if callable(n_max) else n_max
        for i, (s, v) in enumerate(pts[:n]):
            x = cx - L / 2 + s * L
            y = cy + 12 * math.sin(s * 2 * math.pi * 1.2 - T * 4) + v * Hh * worm_profile(s, "tail", "head")
            r = 7 + 2 * math.sin(T * 6 + i)
            d.ellipse([x - r, y - r, x + r, y + r], fill=GLOW, outline=OUTL, width=2)
    return f

def neo_props(frame, d, T, sc):
    lt = T - sc["s"]
    planarian(frame, 540, 1000, 800, T, dots=neo_dots(lambda T: int(clamp((T - sc["s"] - 0.6) / 2.5) * 120)))
    if lt > 0.5: top_label(frame, "NEOBLASTS", 380, YEL, 110)
    if lt > 1.5: put(frame, "up to 30% of cells", 540, 520, 64, WHITE)

def one_props(frame, d, T, sc):
    lt = T - sc["s"]
    gen = int(clamp((lt - 1.5) / 4.5) * 8)
    n = 1 if lt < 1.5 else min(200, 2 ** gen)
    pale = lt < 1.5
    planarian(frame, 540, 1000, 800, T, dots=neo_dots(n))
    put(frame, f"{n} STEM CELL" + ("S" if n > 1 else ""), 540, 560, 80, YEL if n > 1 else WHITE)
    if lt > 0.5: top_label(frame, "ONE CELL", 380, YEL, 100)

def memory_props(frame, d, T, sc):
    lt = T - sc["s"]
    # light bulb on the left
    bx, by = 200, 640
    on = 0.5 + 0.5 * math.sin(T * 5)
    d.ellipse([bx - 70, by - 70, bx + 70, by + 70], fill=(255, 240, 120) if on > 0.3 else (240, 220, 110),
              outline=OUTL, width=6)
    d.rectangle([bx - 30, by + 60, bx + 30, by + 110], fill=(170, 170, 180), outline=OUTL, width=5)
    if lt < 1.4:
        planarian(frame, 600, 1000, 700, T)
        if lt > 0.8: blade(d, 600 + 700 * 0.3, 700 + 200 * clamp((lt - 0.8) / 0.4), 1150)
    else:
        g = clamp((lt - 1.6) / 3.0)
        planarian(frame, 600, 1000, 700, T, body=(0.0, 0.8), grow=g)
        if g > 0.95: put(frame, "I REMEMBER!", 600, 740, 64, YEL)
    if lt > 0.5: top_label(frame, "NEW HEAD, OLD MEMORY?", 380, YEL, 76)

def liver(d, cx, cy, s, frac, T):
    """Cartoon liver; frac = fraction grown (0.3..1)."""
    col = (170, 60, 60)
    full = [(-1.0, -0.2), (-0.7, -0.6), (0.0, -0.75), (0.8, -0.55), (1.0, -0.3), (0.4, 0.2), (-0.3, 0.55),
            (-0.9, 0.35)]
    xs = [p[0] for p in full]
    cut = -1.0 + 2.0 * frac
    pts = [(cx + max(min(x, cut), -1.0) * 220 * s, cy + y * 220 * s) for x, y in full]
    d.polygon(pts, fill=col, outline=OUTL, width=7)
    d.ellipse([cx - 150 * s, cy - 120 * s, cx - 90 * s, cy - 80 * s], fill=(210, 110, 110))

def you_props(frame, d, T, sc):
    lt = T - sc["s"]
    frac = 0.3 + 0.7 * clamp((lt - 1.5) / 4.0)
    liver(d, 600, 1000, 1.2, frac, T)
    put(frame, f"{int(round(frac * 100))}%", 600, 1190, 80, YEL)
    if lt > 0.5: top_label(frame, "YOUR LIVER", 380, YEL, 100)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    # microscope
    mx, my = 800, 1060
    d.rounded_rectangle([mx - 120, my + 220, mx + 120, my + 260], radius=12, fill=(80, 90, 110), outline=OUTL, width=6)
    d.rectangle([mx - 20, my + 30, mx + 20, my + 220], fill=(110, 120, 140), outline=OUTL, width=5)
    d.polygon([(mx - 40, my - 160), (mx + 10, my - 180), (mx + 60, my + 40), (mx + 10, my + 60)],
              fill=(230, 232, 240), outline=OUTL)
    d.rectangle([mx - 90, my + 100, mx + 90, my + 120], fill=(80, 90, 110), outline=OUTL, width=4)
    planarian(frame, mx, my + 85, 120, T, wig=0.3)
    if lt > 0.5: top_label(frame, "BENGALURU LABS", 380, YEL, 92)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # ISS-ish module
    Y = 1240
    d.rounded_rectangle([60, Y, 1020, Y + 120], radius=30, fill=(200, 206, 220), outline=OUTL, width=6)
    for k in range(6):
        d.ellipse([110 + k * 150, Y + 30, 170 + k * 150, Y + 90], fill=(120, 190, 240), outline=OUTL, width=4)
    d.rectangle([0, Y + 30, 60, Y + 90], fill=(60, 80, 160), outline=OUTL, width=4)
    d.rectangle([1020, Y + 30, W, Y + 90], fill=(60, 80, 160), outline=OUTL, width=4)
    g = clamp((lt - 1.0) / 3.0)
    planarian(frame, 470, 980 + 20 * math.sin(T * 1.5), 640, T, left="head", right="head", body=(0.2, 0.8),
              grow=g)
    if lt > 0.5: top_label(frame, "SPACE WORM", 380, YEL, 100)

def kid_peek(T): return (180, 1240, 260)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="meet", s=4.0, e=11.0, bg_fn=lambda T: pond_bg(), clock="POND LIFE", props=meet_props, char="kid",
         pos=kid_peek, look=(0.6, -0.3),
         narr="Meet the PLANARIAN, a flatworm that lives under stones in ponds and streams.", n_at=4.2,
         narr_y=1580, say="Why is it CROSS-EYED?", say_at=7.4, pitch=440),
    dict(id="cut", s=11.0, e=18.0, bg_fn=lambda T: pond_bg(), clock="CUT IT", props=cut_props,
         narr="Cut it in HALF and each piece regrows what's missing. Now you have TWO worms!", n_at=11.2,
         narr_y=1580),
    dict(id="morgan", s=18.0, e=25.0, bg_fn=lambda T: lab_bg(), clock="TINY PIECE", props=morgan_props,
         narr="In 1898, scientist T.H. MORGAN saw a piece just 1/279th of a worm regrow a WHOLE worm.",
         n_at=18.2, narr_y=1580),
    dict(id="neo", s=25.0, e=32.0, bg_fn=lambda T: lab_bg(), clock="THE SECRET", props=neo_props,
         narr="Its secret: stem cells called NEOBLASTS that can turn into ANY body part.", n_at=25.2,
         narr_y=1580),
    dict(id="one", s=32.0, e=39.0, bg_fn=lambda T: lab_bg(), clock="2011", props=one_props,
         narr="In 2011, scientists gave a worm with no stem cells just ONE neoblast. It rebuilt the WHOLE body.",
         n_at=32.2, narr_y=1580),
    dict(id="memory", s=39.0, e=46.0, bg_fn=lambda T: pond_bg(), clock="2013", props=memory_props,
         narr="Worms trained to find food, then beheaded, relearned FASTER after growing a brand-new HEAD.",
         n_at=39.2, narr_y=1580),
    dict(id="you", s=46.0, e=53.0, bg="office", clock="AND YOU?", props=you_props, char="kid",
         pos=(170, 1270, 220), look=(0.6, -0.4),
         narr="YOU can regrow a bit too: a liver can regrow to nearly full size in about 3-4 WEEKS.",
         n_at=46.2, narr_y=1580, say="But not a new ARM!", say_at=49.6, pitch=440),
    dict(id="india", s=53.0, e=TW, bg_fn=lambda T: lab_bg(), clock="INDIA", props=india_props, char="uncle",
         pos=(330, 1060, 360), look=(0.6, 0.2),
         narr="In BENGALURU, labs at inStem and NCBS study planarians to learn how humans might heal better.",
         n_at=53.2, narr_y=1580),
    dict(id="twist", s=TW, e=67.0, bg="space", clock="PLOT TWIST", props=twist_props, char="kid",
         pos=(900, 1110, 200), look=(-0.6, -0.2), twist=True,
         narr="Twist: in 2015, flatworms spent 5 WEEKS on the SPACE STATION. One came back with TWO HEADS!",
         n_at=TW + 0.2, narr_y=1600, say="Which end is the FRONT?", say_at=TW + 3.6, pitch=440),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        planarian(frame, 540, 1350, 620 * p + 2, T)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU COULD REGROW", WHITE)], 110), 730, 0.75, "right"),
        (title([("LIKE THIS WORM?", YEL)], 130), 870, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which part would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("want to regrow?", YEL)], 100), 600, 0.45)],
               row=[("kid", 1), ("fish", 1), ("uncle", 1), ("earth", 1), ("samosa", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("bubbles", 4.3, 0.15, dict(dd=6.0)), ("whoosh", 12.0, 0.4), ("pop", 12.6, 0.3), ("ding", 16.5, 0.2),
        ("pop", 34.0, 0.15), ("pop", 35.0, 0.15), ("pop", 36.0, 0.2), ("pop", 37.0, 0.25),
        ("whoosh", 40.0, 0.4), ("ding", 44.5, 0.2), ("pop", 47.5, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_could_regrow_like_a_planarian")
