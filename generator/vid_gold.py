#!/usr/bin/env python3
"""What if you could turn anything into gold? Facts: lead has 82 protons, gold 79; CERN ALICE (Physical Review C,
published May 2025): in ultra-peripheral 'near-miss' lead-lead collisions, photons knock 3 protons (and at least one
neutron) out of lead, making gold; about 86 billion gold nuclei across LHC Run 2 (2015-2018), about 29 picograms,
peak ~89,000 per second; they exist only for a fraction of a second (sci.news, MaterialDistrict). 1 g / 29 pg = 3.4e10
Run-2s of ~4 years each = ~1.4e11 years, far longer than the 13.8-billion-year age of the universe. Neutron-star
merger GW170817 (17 Aug 2017) may have produced about an Earth mass of gold (NASA HEASARC). World Gold Council: about
224,200 t above-ground stocks (end Q3 2026), a cube ~22.6 m a side. WGC India: households hold up to 24,000-25,000 t
(Business Today, 2019) -> about 11%, ~1 in 9. Twist: King Midas, Greek myth (public domain): his food turned to gold."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 60.0
GOLD = (255, 196, 40)
GOLD_D = (200, 140, 20)
LEAD = (130, 135, 150)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0, gold=False):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    if gold:
        a = np.asarray(spr).astype(np.float32)
        lum = (a[..., :3].mean(axis=2, keepdims=True) / 255.0)
        g = np.array(GOLD, np.float32) * (0.45 + 0.75 * lum)
        a[..., :3] = np.clip(g, 0, 255)
        spr = Image.fromarray(a.astype(np.uint8), "RGBA")
    comp(frame, spr, x - size / 2, y - size / 2)

def bar(d, x, y, s, col=GOLD, dark=GOLD_D):
    """Trapezoid ingot centred at x, y."""
    d.polygon([(x - s, y + 0.35 * s), (x + s, y + 0.35 * s), (x + 0.7 * s, y - 0.35 * s), (x - 0.7 * s, y - 0.35 * s)],
              fill=col, outline=OUTL, width=5)
    d.polygon([(x - 0.7 * s, y - 0.35 * s), (x + 0.7 * s, y - 0.35 * s), (x + 0.6 * s, y - 0.2 * s),
               (x - 0.6 * s, y - 0.2 * s)], fill=dark)
    d.line([(x - 0.4 * s, y), (x - 0.1 * s, y)], fill=(255, 245, 200), width=5)

def nucleus(d, x, y, r, n, col, seed=1):
    import random
    rnd = random.Random(seed)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 50, 80), outline=OUTL, width=5)
    for k in range(n):
        a = rnd.random() * 6.283; rr = (rnd.random() ** 0.5) * (r - 16)
        px, py = x + rr * math.cos(a), y + rr * math.sin(a)
        c = (230, 80, 80) if k % 2 == 0 else (200, 200, 220)
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=c, outline=OUTL, width=2)
    d.ellipse([x - r - 10, y - r - 10, x + r + 10, y + r + 10], outline=col, width=8)

# ---------------------------------------------------------------- props
def atoms_props(frame, d, T, sc):
    lt = T - sc["s"]
    nucleus(d, 290, 960, 170, 60, LEAD, 3)
    lab_at(frame, "LEAD: 82", 290, 1210, WHITE, 60)
    if lt > 1.6:
        nucleus(d, 790, 960, 160, 56, GOLD, 4)
        lab_at(frame, "GOLD: 79", 790, 1210, YEL, 60)
    if lt > 3.0:
        for k in range(3):
            t = clamp((lt - 3.0 - 0.25 * k) / 1.2)
            x = 290 + 240 * t + 30 * k; y = 960 - 330 * t - 20 * k
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(230, 80, 80), outline=OUTL, width=4)
        top_label(frame, "-3 PROTONS", 420, YEL, 80)

def ring(d, cx, cy, rx, ry):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(120, 180, 255), width=26)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=OUTL, width=4)
    d.ellipse([cx - rx + 22, cy - ry + 22, cx + rx - 22, cy + ry - 22], outline=OUTL, width=4)

def cern_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, rx, ry = 540, 1000, 400, 230
    ring(d, cx, cy, rx, ry)
    for k, sgn in ((0, 1), (1, -1)):
        a = sgn * T * 3.0 + k * 0.4
        x = cx + (rx - 11) * math.cos(a); y = cy + (ry - 11) * math.sin(a)
        col = GOLD if (lt > 2.5 and k == 0) else LEAD
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=col, outline=OUTL, width=4)
    lab_at(frame, "27 KM RING", 540, 1000, WHITE, 52)
    if lt > 0.4: top_label(frame, "LARGE HADRON COLLIDER", 400, WHITE, 60)

def amount_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a sea of tiny gold dots...
    p = ease_out(clamp((lt - 0.3) / 2.0))
    n = int(400 * p)
    for k in range(n):
        x = 120 + (k * 97) % 840; y = 700 + ((k * 53) % 520)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=GOLD)
    if lt > 1.0: top_label(frame, "86,000,000,000 GOLD ATOMS", 400, YEL, 56)
    if lt > 3.4:
        d.rounded_rectangle([290, 1250, 790, 1330], radius=20, fill=(30, 30, 50), outline=YEL, width=5)
        lab_at(frame, "TOTAL: 29 PICOGRAMS", 540, 1290, WHITE, 48)

def short_props(frame, d, T, sc):
    lt = T - sc["s"]
    x, y = 540, 980
    if lt < 1.8:
        nucleus(d, x, y, 150, 52, GOLD, 5)
    else:
        q = ease_out(clamp((lt - 1.8) / 1.2))
        import random
        rnd = random.Random(9)
        for k in range(40):
            a = rnd.random() * 6.283; sp = 60 + rnd.random() * 380
            px, py = x + sp * q * math.cos(a), y + sp * q * math.sin(a)
            c = (230, 80, 80) if k % 2 == 0 else (200, 200, 220)
            d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=c, outline=OUTL, width=2)
        top_label(frame, "POOF!", 420, YEL, 110)

def gram_props(frame, d, T, sc):
    lt = T - sc["s"]
    bar(d, 540, 980, 110)
    lab_at(frame, "1 GRAM", 540, 1100, YEL, 60)
    if lt > 1.5:
        yrs = int(min(1.0, (lt - 1.5) / 3.0) * 140)
        lab_at(frame, f"~{yrs} BILLION YEARS...", 540, 760, WHITE, 64)
    if lt > 4.8:
        lab_at(frame, "UNIVERSE: 13.8 BILLION", 540, 1220, WHITE, 48)

def stars_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_in = clamp(lt / 2.5)
    sep = 330 * (1 - p)
    for sgn in (-1, 1):
        a = T * 6 * sgn
        x = 540 + sgn * sep * math.cos(T * 4); y = 960 + sep * math.sin(T * 4) * 0.4 * sgn
        if p < 1:
            d.ellipse([x - 70, y - 70, x + 70, y + 70], fill=(200, 220, 255), outline=OUTL, width=6)
    if p >= 1:
        q = ease_out(clamp((lt - 2.5) / 1.0))
        r = 60 + 240 * q
        d.ellipse([540 - r, 960 - r, 540 + r, 960 + r], fill=(255, 230, 140), outline=GOLD, width=10)
        if lt > 3.2:
            mini(frame, "earth", 540, 930, 200, T, 0)
            comp(frame, *(lambda s: (s, 540 - s.width / 2, 1060))(label("1 EARTH OF GOLD?", 56, YEL)))
    if lt > 0.3: top_label(frame, "NEUTRON STARS, 2017", 400, WHITE, 62)

def cube_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp((lt - 0.4) / 0.8))
    s = 300 * p + 2; x, y = 470, 1000
    o = 0.4 * s
    d.polygon([(x - s / 2, y - s / 2), (x - s / 2 + o, y - s / 2 - o), (x + s / 2 + o, y - s / 2 - o), (x + s / 2, y - s / 2)],
              fill=(255, 220, 100), outline=OUTL, width=5)
    d.polygon([(x + s / 2, y - s / 2), (x + s / 2 + o, y - s / 2 - o), (x + s / 2 + o, y + s / 2 - o), (x + s / 2, y + s / 2)],
              fill=GOLD_D, outline=OUTL, width=5)
    d.rectangle([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=GOLD, outline=OUTL, width=5)
    if lt > 1.4:
        mini(frame, "kid", 220, 1110, 110, T, 1, (0.5, -0.4))
        lab_at(frame, "~23 m", x, y, OUTL if False else WHITE, 64)
    if lt > 2.4: top_label(frame, "ALL GOLD EVER MINED", 400, WHITE, 64)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    k_on = int(clamp((lt - 0.4) / 2.0) * 9)
    for k in range(9):
        r, c = divmod(k, 3)
        x = 280 + 260 * c; y = 760 + 160 * r
        if k < k_on:
            if k == 4 and lt > 2.8:
                bar(d, x, y, 95 + 6 * math.sin(T * 6))
            else:
                bar(d, x, y, 85, (190, 175, 130), (150, 135, 95))
    if lt > 2.8: lab_at(frame, "1 IN 9 BARS", 540, 1270, YEL, 64)
    if lt > 0.3: top_label(frame, "INDIAN HOMES", 400, WHITE, 70)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "uncle", 540, 900, 380, T, "crown_angry" if lt > 3.0 else "crown", (0.3, 0.4),
         clamp(0.5 + 0.6 * math.sin(T * 22)) if lt > 3.0 else 0)
    g = lt > 2.2
    mini(frame, "samosa", 800, 1170, 200, T, 1, (0, 0), gold=g)
    mini(frame, "chai", 290, 1170, 190, T, 1, (0, 0), gold=g)
    if g:
        for k in range(6):
            a = T * 2 + k
            x = 800 + 130 * math.cos(a); y = 1170 + 110 * math.sin(a)
            d.line([(x - 12, y), (x + 12, y)], fill=WHITE, width=4); d.line([(x, y - 12), (x, y + 12)], fill=WHITE, width=4)
    if lt > 0.5: top_label(frame, "KING MIDAS", 400, YEL, 80)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="atoms", s=4.0, e=11.0, bg="space", clock="THE RECIPE", props=atoms_props,
         narr="LEAD has 82 PROTONS. GOLD has 79. Knock out 3, and lead becomes GOLD.", n_at=4.2, narr_y=1490),
    dict(id="cern", s=11.0, e=18.0, bg="space", clock="REAL ALCHEMY", props=cern_props,
         narr="In 2025, CERN scientists showed their giant collider really turns LEAD into GOLD.", n_at=11.2,
         narr_y=1490),
    dict(id="amount", s=18.0, e=25.0, bg="night", clock="THE HAUL", props=amount_props,
         narr="From 2015 to 2018 it made 86 BILLION gold atoms, weighing just 29 PICOGRAMS.", n_at=18.2,
         narr_y=1490),
    dict(id="short", s=25.0, e=32.0, bg="night", clock="BLINK", props=short_props,
         narr="And each one broke apart in a TINY FRACTION of a second.", n_at=25.2, narr_y=1490),
    dict(id="gram", s=32.0, e=39.0, bg="space", clock="ONE GRAM", props=gram_props,
         narr="At that speed, ONE GRAM of gold would take longer than the AGE OF THE UNIVERSE.", n_at=32.2,
         narr_y=1490),
    dict(id="stars", s=39.0, e=46.0, bg="space", clock="COSMIC MINT", props=stars_props,
         narr="Gold can be forged when NEUTRON STARS crash. One crash in 2017 may have made an EARTH'S WORTH!",
         n_at=39.2, narr_y=1500),
    dict(id="cube", s=46.0, e=53.0, bg="day", clock="EVERY GRAM", props=cube_props,
         narr="All gold ever mined, about 224,000 TONNES, fits in a CUBE about 23 METRES wide.", n_at=46.2,
         narr_y=1490),
    dict(id="india", s=53.0, e=TW, bg="living", clock="SHAADI SEASON", props=india_props,
         narr="Indian homes hold up to 25,000 TONNES of it. That's about 1 IN 9 bars!", n_at=53.2,
         narr_y=1490),
    dict(id="twist", s=TW, e=67.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: in the Greek myth, King MIDAS got the golden touch, and his FOOD turned to gold too!",
         n_at=TW + 0.2, narr_y=1490),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        for k, x in enumerate((360, 540, 720)):
            bar(d, x, 1240 + (40 if k != 1 else 0), 90 * p + 1)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU COULD MAKE", WHITE)], 120), 690, 0.75, "right"),
        (title([("GOLD?", YEL)], 190), 840, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("turn into gold?", WHITE)], 96), 600, 0.45)],
               row=[("kid", 1), ("uncle", "crown"), ("samosa", 1), ("chai", 1), ("ladoo", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=39.0), dict(t0=39.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("pop", 5.6, 0.3), ("whoosh", 7.0, 0.2), ("ding", 7.3, 0.2), ("whoosh", 13.5, 0.2),
        ("ding", 21.4, 0.2), ("pop", 26.8, 0.35), ("tick", 34.0, 0.2), ("ding", 36.8, 0.2),
        ("boom", 41.5, 0.3), ("pop", 47.0, 0.3), ("ding", 55.8, 0.2), ("ding", TW + 2.2, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_could_make_gold")
