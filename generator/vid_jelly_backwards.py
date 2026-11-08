#!/usr/bin/env python3
"""What if you aged backwards like the immortal jellyfish? Facts: Turritopsis dohrnii is about 4.5 mm across, smaller
than a pinky nail, with a bright-red stomach and up to 90 white tentacles (AMNH 'The Immortal Jellyfish'; The
Biologist / Royal Society of Biology). When physically damaged or starved the adult (medusa) reverts to a polyp,
which buds new medusae genetically identical to the injured adult; the cellular mechanism is transdifferentiation,
a specialised cell becoming a different type of cell (AMNH). Usual hydrozoan life cycle: polyp attached to a surface
buds free-swimming medusae (AMNH). Shin Kubota's 2009 paper describes lab specimens 'rejuvenated four times' (The
Biologist). Jellyfish are about 95% water and lack brains, blood and hearts (NOAA Ocean Service). 'Immortality' is a
figurative description (AMNH); they can still be eaten. Twist: in the 1980s Christian Sommer forgot medusae in a jar in
Ferdinando Boero's lab and later found polyps instead (The Biologist / RSB)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 60.0
BELL = (236, 226, 255)
BELL_D = (200, 186, 240)
GUT = (230, 50, 70)
POLYP = (250, 214, 200)

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
def sea_bg():
    if "sea" not in _bgc:
        img = grad([(0, (40, 120, 190)), (0.6, (20, 70, 130)), (1, (12, 40, 84))], W, H)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1320, W, H], fill=(70, 74, 96))
        rng = np.random.default_rng(6)
        for k in range(14):
            x = rng.uniform(0, W); r = rng.uniform(50, 120)
            d.ellipse([x - r, 1300 - r * 0.5, x + r, 1300 + r * 0.5], fill=(92, 96, 120))
        for k in range(40):
            x = rng.uniform(0, W); y = rng.uniform(0, 1250); r = rng.uniform(2, 5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 200, 240))
        _bgc["sea"] = img
    return _bgc["sea"]

def lab_bg():
    if "lab" not in _bgc:
        img = grad([(0, (226, 236, 246)), (1, (196, 210, 228))], W, H)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1320, W, H], fill=(150, 160, 176))
        d.rectangle([0, 1310, W, 1330], fill=(110, 118, 134))
        _bgc["lab"] = img
    return _bgc["lab"]

# ---------------------------------------------------------------- jellyfish
def jelly(frame, cx, cy, s, T, face=True, squash=0.0, ntent=16):
    """Medusa: bell centred at (cx, cy), width ~ 2*s."""
    if s < 3: return
    d = ImageDraw.Draw(frame)
    pulse = 0.06 * math.sin(T * 4)
    bw = s * (1 + pulse); bh = s * (0.85 - pulse - 0.4 * squash)
    ow = max(2, int(s / 30))
    # tentacles
    for k in range(ntent):
        x0 = cx - bw * 0.85 + k * (1.7 * bw / max(1, ntent - 1))
        pts = []
        ln = s * (1.3 - 0.6 * squash)
        for j in range(12):
            t = j / 11
            pts.append((x0 + s * 0.08 * math.sin(T * 3 + k * 0.7 + t * 5), cy + t * ln))
        d.line(pts, fill=WHITE, width=max(2, int(s / 28)))
    # bell
    d.chord([cx - bw, cy - bh, cx + bw, cy + bh], 180, 360, fill=BELL, outline=OUTL, width=ow)
    d.ellipse([cx - bw, cy - bh * 0.18, cx + bw, cy + bh * 0.18], fill=BELL_D, outline=OUTL, width=ow)
    # red stomach
    gr = s * 0.32
    d.ellipse([cx - gr, cy - bh * 0.62, cx + gr, cy - bh * 0.62 + gr * 1.5], fill=GUT, outline=OUTL, width=ow)
    if face and s > 40:
        for ex in (-0.42, 0.42):
            x = cx + ex * bw; y = cy - bh * 0.45; r = s * 0.11
            d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE, outline=OUTL, width=max(2, ow - 1))
            pr = r * 0.55
            d.ellipse([x - pr, y - pr + r * 0.2, x + pr, y + pr + r * 0.2], fill=OUTL)
        d.arc([cx - s * 0.18, cy - bh * 0.32, cx + s * 0.18, cy - bh * 0.12], 20, 160, fill=OUTL,
              width=max(2, ow - 1))

def polyp(frame, x, ybase, h, T, buds=0):
    if h < 4: return
    d = ImageDraw.Draw(frame)
    w = max(6, h * 0.12)
    sway = math.sin(T * 1.8 + x) * h * 0.08
    top = (x + sway, ybase - h)
    d.line([(x, ybase), top], fill=OUTL, width=int(w + 6))
    d.line([(x, ybase), top], fill=POLYP, width=int(w))
    # crown of tentacles
    for k in range(9):
        a = math.pi + (k / 8) * math.pi
        ln = h * 0.28
        ex = top[0] + math.cos(a) * ln; ey = top[1] + math.sin(a) * ln * 0.9
        d.line([top, (ex, ey)], fill=WHITE, width=max(2, int(w * 0.35)))
    r = w * 0.9
    d.ellipse([top[0] - r, top[1] - r, top[0] + r, top[1] + r], fill=GUT, outline=OUTL, width=2)
    for b in range(buds):
        by = ybase - h * (0.35 + 0.18 * b)
        bx = x + sway * (0.35 + 0.18 * b) + (w + 16) * (1 if b % 2 == 0 else -1)
        jelly(frame, bx, by, 18, T, face=False, ntent=5)

def rock(d, cx, cy, w, h):
    d.ellipse([cx - w, cy - h, cx + w, cy + h], fill=(110, 104, 120), outline=OUTL, width=5)

def blob(d, cx, cy, r, T):
    w = r * (1 + 0.06 * math.sin(T * 5))
    d.ellipse([cx - w, cy - r * 0.8, cx + w, cy + r * 0.8], fill=BELL_D, outline=OUTL, width=4)
    d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=GUT)

# ---------------------------------------------------------------- props
def meet_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    jelly(frame, 580 + 40 * math.sin(T * 0.7), 1030 + 20 * math.sin(T * 1.3), 200 * p, T)
    if lt > 0.5: top_label(frame, "IMMORTAL JELLYFISH", 380, YEL, 84)
    if lt > 1.2: put(frame, "Turritopsis dohrnii", 540, 490, 54, WHITE)

def life_props(frame, d, T, sc):
    lt = T - sc["s"]
    rock(d, 230, 1320, 170, 70)
    g = clamp(lt / 1.2)
    polyp(frame, 230, 1270, 330 * g, T, buds=2 if lt > 1.2 else 0)
    # a baby jelly drifts up and grows
    q = clamp((lt - 2.0) / 3.5)
    if lt > 2.0:
        jelly(frame, 330 + 380 * q, 1050 - 300 * q, 20 + 130 * q, T, face=q > 0.4)
    if lt > 5.6:
        put(frame, "...then dies", 720, 1120, 60, WHITE)
    if lt > 0.5: top_label(frame, "A NORMAL JELLY LIFE", 380, YEL, 80)

def reverse_props(frame, d, T, sc):
    lt = T - sc["s"]
    rock(d, 540, 1320, 260, 70)
    if lt < 3.0:
        q = clamp((lt - 0.4) / 2.6)
        jelly(frame, 540, 820 + 360 * q, 200 * (1 - 0.6 * q), T, squash=q, face=True)
    elif lt < 4.3:
        blob(d, 540, 1220, 70, T)
    else:
        g = clamp((lt - 4.3) / 1.4)
        blob(d, 540, 1240, 60 * (1 - g) + 30, T)
        polyp(frame, 540, 1250, 380 * g, T)
    if lt > 0.5: top_label(frame, "REWIND!", 380, YEL, 120)

def age_clock(T):
    lt = T - 25.0
    a = 70 - 69 * clamp((lt - 0.8) / 3.0)
    return f"AGE {int(round(a))}"

def dadaji_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp((lt - 0.8) / 3.0)
    if q < 0.5:
        mini(frame, "uncle", 540, 1060, 560 * (1 - q * 0.6), T, look=(0, 0.2))
    else:
        mini(frame, "kid", 540, 1120, 300 + 240 * (q - 0.5), T, look=(0, 0.2))
    # rewind symbol drawn as triangles
    x, y = 860, 720
    for k in range(2):
        d.polygon([(x - k * 60, y - 40), (x - k * 60, y + 40), (x - 60 - k * 60, y)], fill=YEL, outline=OUTL)
    if lt > 0.5: top_label(frame, "DADAJI ON REWIND", 380, YEL, 92)

def cell(d, x, y, r, col, kind, T, k):
    w = r * (1 + 0.05 * math.sin(T * 4 + k))
    if kind == "muscle":
        d.ellipse([x - w * 1.6, y - r * 0.55, x + w * 1.6, y + r * 0.55], fill=col, outline=OUTL, width=4)
    elif kind == "nerve":
        for a in range(5):
            ang = a * 2 * math.pi / 5 + 0.3
            d.line([(x, y), (x + math.cos(ang) * r * 1.7, y + math.sin(ang) * r * 1.7)], fill=OUTL, width=10)
            d.line([(x, y), (x + math.cos(ang) * r * 1.7, y + math.sin(ang) * r * 1.7)], fill=col, width=5)
        d.ellipse([x - w * 0.8, y - w * 0.8, x + w * 0.8, y + w * 0.8], fill=col, outline=OUTL, width=4)
    else:
        d.ellipse([x - w, y - w, x + w, y + w], fill=col, outline=OUTL, width=4)
    d.ellipse([x - r * 0.25, y - r * 0.25, x + r * 0.25, y + r * 0.25], fill=OUTL)

def cells_props(frame, d, T, sc):
    lt = T - sc["s"]
    st = int(clamp((lt - 1.0) / 4.5) * 3)
    kinds = ["muscle", "round", "nerve", "nerve"]
    cols = [(240, 120, 120), (200, 200, 230), (250, 210, 90), (250, 210, 90)]
    rng = np.random.default_rng(2)
    for k in range(6):
        x = 220 + (k % 3) * 320; y = 760 + (k // 3) * 300
        kk = min(3, st + (1 if k % 2 and st > 0 else 0)) if st < 3 else 2
        cell(d, x + 10 * math.sin(T + k), y, 70, cols[kk], kinds[kk], T, k)
    put(frame, ["MUSCLE CELL", "RESET...", "NEW JOB!", "NEW JOB!"][st], 540, 1220, 72, WHITE)
    if lt > 0.5: top_label(frame, "CELLS SWITCH JOBS", 380, YEL, 88)

def copies_props(frame, d, T, sc):
    lt = T - sc["s"]
    rock(d, 540, 1320, 300, 70)
    polyp(frame, 400, 1270, 300, T)
    polyp(frame, 680, 1270, 260, T)
    n = int(clamp((lt - 0.8) / 4.5) * 7)
    for k in range(n):
        q = clamp((lt - 0.8 - k * 0.64) / 2.5)
        x = 200 + (k * 137) % 700
        y = 1050 - 330 * q - (k % 3) * 40
        jelly(frame, x, y, 30 + 40 * q, T + k, face=True, ntent=8)
    if lt > 0.5: top_label(frame, "COPIES!", 380, YEL, 120)

def repeat_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = 1 + min(3, int(max(0, lt - 0.8) / 1.4))
    ph = (max(0, lt - 0.8) % 1.4) / 1.4
    if ph < 0.5:
        jelly(frame, 540, 900, 200 * (1 - ph), T, face=True)
    else:
        rock(d, 540, 1320, 200, 70)
        polyp(frame, 540, 1270, 320 * (ph - 0.5) * 2, T)
    put(frame, f"REWIND x{n}", 540, 520, 96, WHITE)
    if lt > 0.5: top_label(frame, "AGAIN AND AGAIN", 380, YEL, 96)

def fish_props(frame, d, T, sc):
    lt = T - sc["s"]
    jx = 700 + 60 * math.sin(T * 1.1)
    jelly(frame, jx, 860, 150, T, face=True)
    fx = -200 + 260 * lt
    if lt > 1.0:
        mini(frame, "fish", min(fx, jx - 260), 1000, 320, T, look=(1, 0))
    put(frame, "95% WATER", 540, 520, 76, WHITE)
    if lt > 0.5: top_label(frame, "NOT INVINCIBLE", 380, YEL, 100)

def labjar(d, cx, cy, T):
    d.rounded_rectangle([cx - 190, cy - 280, cx + 190, cy + 220], radius=50, fill=(190, 230, 250), outline=OUTL,
                        width=7)
    d.rectangle([cx - 170, cy - 180, cx + 170, cy + 200], fill=(120, 190, 230))
    d.rounded_rectangle([cx - 210, cy - 330, cx + 210, cy - 270], radius=14, fill=(160, 170, 190), outline=OUTL,
                        width=6)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    labjar(d, 600, 1130, T)
    if lt < 2.2:
        for k in range(3):
            jelly(frame, 520 + k * 90, 1030 + 30 * math.sin(T * 2 + k), 40, T + k, face=True, ntent=8)
    else:
        g = clamp((lt - 2.2) / 1.2)
        for k in range(4):
            polyp(frame, 470 + k * 80, 1320, 150 * g * (0.8 + 0.2 * (k % 2)), T)
    if lt > 0.5: top_label(frame, "FOUND BY ACCIDENT", 380, YEL, 86)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="meet", s=4.0, e=11.0, bg_fn=lambda T: sea_bg(), clock="DEEP BLUE", props=meet_props, char="kid",
         pos=(160, 1180, 220), look=(0.6, -0.3),
         narr="Meet the IMMORTAL JELLYFISH: about 4.5 MM wide, smaller than your pinky nail.", n_at=4.2,
         narr_y=1580, say="So TINY!", say_at=7.8, pitch=440),
    dict(id="life", s=11.0, e=18.0, bg_fn=lambda T: sea_bg(), clock="USUALLY", props=life_props,
         narr="Most jellies start as a POLYP stuck to a rock, bud off swimmers, grow up and DIE.", n_at=11.2,
         narr_y=1580),
    dict(id="reverse", s=18.0, e=25.0, bg_fn=lambda T: sea_bg(), clock="BUT THIS ONE", props=reverse_props,
         narr="Hurt or starve THIS one and it sinks, shrinks into a blob and turns back into a POLYP.",
         n_at=18.2, narr_y=1580),
    dict(id="dadaji", s=25.0, e=32.0, bg="living", clock=age_clock, props=dadaji_props,
         narr="That's like DADAJI turning back into a BABY and growing up all over AGAIN.", n_at=25.2,
         narr_y=1580),
    dict(id="cells", s=32.0, e=39.0, bg_fn=lambda T: lab_bg(), clock="HOW?", props=cells_props,
         narr="Its cells SWITCH JOBS, one kind turning into another. Scientists call it TRANSDIFFERENTIATION.",
         n_at=32.2, narr_y=1580),
    dict(id="copies", s=39.0, e=46.0, bg_fn=lambda T: sea_bg(), clock="SURPRISE", props=copies_props,
         narr="The new polyp buds MANY jellies with the SAME genes. One old jelly, a crowd of COPIES!",
         n_at=39.2, narr_y=1580),
    dict(id="repeat", s=46.0, e=53.0, bg_fn=lambda T: sea_bg(), clock="2009", props=repeat_props,
         narr="In a 2009 study in JAPAN, lab jellies rewound their lives FOUR times.", n_at=46.2,
         narr_y=1580),
    dict(id="fish", s=53.0, e=TW, bg_fn=lambda T: sea_bg(), clock="CATCH", props=fish_props,
         narr="No brain, no heart, and fish still EAT it. 'Immortal' just means it can RESTART.",
         n_at=53.2, narr_y=1580),
    dict(id="twist", s=TW, e=67.0, bg_fn=lambda T: lab_bg(), clock="PLOT TWIST", props=twist_props,
         char="kid", pos=(170, 1180, 240), look=(0.6, -0.2), twist=True,
         narr="Twist: in the 1980s, a student FORGOT jellies in a lab jar and came back to find POLYPS!",
         n_at=TW + 0.2, narr_y=1600, say="Best mistake EVER!", say_at=TW + 3.8, pitch=440),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        jelly(frame, 540, 1260, 170 * p, T)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU AGED", WHITE)], 130), 730, 0.75, "right"),
        (title([("BACKWARDS?", YEL)], 150), 880, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("If ", WHITE), ("YOU", YEL), (" could restart,", WHITE)], 90), 470, 0.15),
                      (title([("which age would you pick?", YEL)], 80), 600, 0.45)],
               row=[("kid", 1), ("fish", 1), ("uncle", 1), ("earth", 1), ("ladoo", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("bubbles", 4.3, 0.15, dict(dd=6.0)), ("powerdown", 19.0, 0.25), ("pop", 23.0, 0.25),
        ("whoosh", 26.0, 0.4), ("ding", 29.0, 0.2), ("pop", 40.5, 0.15), ("pop", 41.5, 0.15),
        ("pop", 42.5, 0.2), ("splash", 54.5, 0.3), ("pop", 62.4, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_aged_backwards")
