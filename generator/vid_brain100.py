#!/usr/bin/env python3
"""What if you used 100% of your brain? Facts: the 10% idea is a myth (MIT McGovern Institute 2024: "100 percent a
myth"; Scientific American: imaging shows most regions are continually active over 24 hours, "we use virtually every
part of the brain", and "at any given moment all of the brain's regions are not concurrently firing"; even in sleep
areas such as the frontal cortex stay active). The brain is ~2% of body weight but uses ~20% of the body's
calories (MIT McGovern; Univ. of Plymouth: ~1.5 kg, ~2% of body weight). Runs on about 20 watts (Physics Factbook,
hypertextbook.com; IFLScience). About 86 billion neurons (Azevedo et al. 2009, J. Comp. Neurol., PubMed 19226510).
A seizure is a sudden, uncontrolled burst of electrical activity in the brain (Mayo Clinic). Twist: brain tissue
has no pain receptors (nociceptors), so some brain surgery is done with the patient awake (BrainFacts.org 2021;
Mayo Clinic 'Awake brain surgery'; the scalp is numbed)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
PINK, PINK_D, GLOW = (240, 170, 190), (200, 110, 140), (255, 214, 60)

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

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

# six "regions" inside the brain outline, as (dx, dy, rx, ry) in units of r
REG = [(-0.55, -0.15, 0.36, 0.42), (-0.12, -0.35, 0.36, 0.3), (0.35, -0.3, 0.34, 0.32),
       (0.62, 0.1, 0.3, 0.3), (0.12, 0.2, 0.38, 0.3), (-0.4, 0.3, 0.32, 0.25)]

def brain(d, cx, cy, r, lit=(), col=GLOW):
    d.ellipse([cx - r, cy - 0.72 * r, cx + r, cy + 0.72 * r], fill=PINK, outline=OUTL, width=8)
    for i, (dx, dy, rx, ry) in enumerate(REG):
        f = col if i in lit else (232, 150, 176)
        d.ellipse([cx + (dx - rx) * r, cy + (dy - ry) * r, cx + (dx + rx) * r, cy + (dy + ry) * r], fill=f)
    for k in range(4):
        d.arc([cx - 0.85 * r + k * 0.4 * r, cy - 0.55 * r, cx - 0.35 * r + k * 0.4 * r, cy + 0.05 * r], 200, 340,
              fill=PINK_D, width=7)
        d.arc([cx - 0.7 * r + k * 0.4 * r, cy - 0.05 * r, cx - 0.2 * r + k * 0.4 * r, cy + 0.5 * r], 200, 340,
              fill=PINK_D, width=7)
    d.ellipse([cx - r, cy - 0.72 * r, cx + r, cy + 0.72 * r], outline=OUTL, width=8)
    # brain stem
    d.rounded_rectangle([cx + 0.1 * r, cy + 0.6 * r, cx + 0.32 * r, cy + 0.95 * r], radius=int(0.1 * r),
                        fill=PINK, outline=OUTL, width=6)

def meter(d, frame, x, y, w, h, frac, lab, col=YEL):
    d.rounded_rectangle([x, y, x + w, y + h], radius=20, fill=(40, 40, 60), outline=OUTL, width=6)
    d.rounded_rectangle([x + 8, y + 8, x + 8 + max(6, (w - 16) * frac), y + h - 8], radius=14, fill=col)
    lab_at(frame, lab, x + w / 2, y - 50, WHITE, 50)

# ---------------------------------------------------------------- props
def myth_props(frame, d, T, sc):
    lt = T - sc["s"]
    blink = int(T * 3) % 2 == 0
    brain(d, 540, 860, 270, lit=(1,) if blink or lt < 2.5 else ())
    if lt > 0.6: lab_at(frame, "ONLY 10%?", 540, 560, YEL, 100)
    if lt > 2.6:
        mini(frame, "kid", 540, 1270, 230, T, 1, (0, -0.4))
        lab_at(frame, "SUPERPOWERS?", 540, 1105, WHITE, 60)

def scan_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = min(6, int(max(0, lt - 0.5) / 0.7) + 1)
    flick = int(T * 8) % 6
    lit = set(range(n)) if n < 6 else {i for i in range(6) if i != flick}
    brain(d, 540, 950, 320, lit=lit)
    top_label(frame, "BRAIN SCAN, ALL DAY", 400, WHITE, 64)
    if lt > 4.6: lab_at(frame, "EVERY PART WORKS", 540, 1290, YEL, 64)

def sleep_props(frame, d, T, sc):
    lt = T - sc["s"]
    # bed
    d.rounded_rectangle([170, 1180, 910, 1290], radius=30, fill=(120, 150, 220), outline=OUTL, width=7)
    d.rounded_rectangle([200, 1130, 420, 1200], radius=30, fill=WHITE, outline=OUTL, width=6)
    spr = draw_char("kid", 300, T, 0, True, (0, 0), 1).rotate(90, expand=True)
    comp(frame, spr, 300 - spr.width / 2, 1110 - spr.height / 2)
    for k in range(3):
        a = (T * 0.8 + k / 3) % 1
        lab_at(frame, "Z", 420 + 60 * k + 40 * a, 980 - 140 * a, WHITE, 50 + 18 * k)
    # thought bubble with a busy brain
    for i, (x, y, r) in enumerate(((520, 920, 18), (580, 860, 28))):
        d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE, outline=OUTL, width=5)
    d.ellipse([480, 520, 1000, 840], fill=WHITE, outline=OUTL, width=7)
    lit = {i for i in range(6) if (int(T * 5) + i * 2) % 3 != 0}
    brain(d, 740, 680, 190, lit=lit)
    if lt > 2.0: top_label(frame, "STILL BUSY", 400, YEL, 72)

def energy_props(frame, d, T, sc):
    lt = T - sc["s"]
    p1 = ease_out(clamp((lt - 0.5) / 0.8)); p2 = ease_out(clamp((lt - 2.6) / 1.0))
    brain(d, 540, 560, 140, lit=(0, 2, 4))
    meter(d, frame, 140, 860, 800, 110, 0.02 * p1, "BODY WEIGHT")
    if lt > 0.8: lab_at(frame, "2%", 860, 915, WHITE, 60)
    if lt > 2.4:
        meter(d, frame, 140, 1130, 800, 110, 0.20 * p2, "ENERGY USED", (255, 120, 80))
        if lt > 3.4: lab_at(frame, "20%", 860, 1185, YEL, 60)

def bulb_props(frame, d, T, sc):
    lt = T - sc["s"]
    on = lt > 1.0
    if on:
        for k in range(10):
            a = k * math.pi / 5 + T * 0.4
            r0, r1 = 230, 290 + 15 * math.sin(T * 6 + k)
            d.line([(540 + r0 * math.cos(a), 880 + r0 * math.sin(a)),
                    (540 + r1 * math.cos(a), 880 + r1 * math.sin(a))], fill=GLOW, width=10)
    d.ellipse([370, 710, 710, 1050], fill=(255, 236, 140) if on else (220, 220, 230), outline=OUTL, width=8)
    d.rounded_rectangle([460, 1030, 620, 1170], radius=14, fill=(160, 160, 175), outline=OUTL, width=7)
    for y in (1065, 1100, 1135):
        d.line([(462, y), (618, y)], fill=OUTL, width=4)
    brain(d, 540, 880, 120, lit=(0, 1, 2, 3, 4, 5) if on else ())
    if on: lab_at(frame, "ABOUT 20 WATTS", 540, 480, YEL, 80)
    if lt > 3.0: lab_at(frame, "DAY AND NIGHT", 540, 1260, WHITE, 60)

rng = np.random.default_rng(7)
NODES = [(int(x), int(y)) for x, y in zip(rng.uniform(150, 930, 46), rng.uniform(560, 1260, 46))]
EDGES = []
for i, a in enumerate(NODES):
    ds = sorted(range(len(NODES)), key=lambda j: (NODES[j][0] - a[0]) ** 2 + (NODES[j][1] - a[1]) ** 2)
    EDGES += [(i, j) for j in ds[1:3]]

def net(d, lit_fn):
    for i, j in EDGES:
        d.line([NODES[i], NODES[j]], fill=(150, 130, 190), width=4)
    for i, (x, y) in enumerate(NODES):
        on = lit_fn(i)
        r = 20 if on else 14
        d.ellipse([x - r, y - r, x + r, y + r], fill=GLOW if on else (200, 180, 230), outline=OUTL, width=4)

def neuron_props(frame, d, T, sc):
    lt = T - sc["s"]
    net(d, lambda i: (int(T * 6) * 7 + i * 13) % 46 < 5)
    v = int(86 * ease_out(clamp((lt - 0.4) / 2.2)))
    lab_at(frame, f"{v} BILLION", 540, 430, YEL, 96)
    if lt > 3.4: lab_at(frame, "ONLY SOME FIRE AT ONCE", 540, 1300, WHITE, 56)

def burst_props(frame, d, T, sc):
    lt = T - sc["s"]
    allon = lt > 1.2
    net(d, (lambda i: True) if allon else (lambda i: (int(T * 6) * 7 + i * 13) % 46 < 5))
    if allon and lt <= 3.2:
        lab_at(frame, "ALL AT ONCE?", 540, 430, (255, 120, 80), 90)
    if lt > 3.2:
        lab_at(frame, "NOT A SUPERPOWER", 540, 430, YEL, 80)

def burst_overlay(frame, T, sc):
    lt = T - sc["s"]
    if 1.2 < lt < 3.0 and int(T * 10) % 2 == 0:
        return Image.blend(frame, Image.new("RGBA", (W, H), (255, 240, 200, 255)), 0.18)
    return frame

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    brain(d, 540, 960, 230, lit=(0, 1, 2, 3, 4, 5) if int(T * 3) % 2 else (1, 3, 5))
    if lt > 0.8:
        d.rounded_rectangle([170, 1190, 910, 1300], radius=30, fill=(40, 30, 60), outline=OUTL, width=6)
        lab_at(frame, "NO PAIN SENSORS", 540, 1245, YEL, 62)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="myth", s=4.0, e=11.0, bg="office", clock="THE MYTH", props=myth_props,
         narr="They say we use only 10% of our BRAIN. What if you used 100%?", n_at=4.2,
         narr_y=1530),
    dict(id="scan", s=11.0, e=18.0, bg="night", clock="REALITY CHECK", props=scan_props,
         narr="Brain scans show VIRTUALLY EVERY PART of your brain gets used each day.", n_at=11.2,
         narr_y=1530),
    dict(id="sleep", s=18.0, e=25.0, bg="bedroom", clock="2 AM", props=sleep_props,
         narr="Even while you SLEEP, big parts of your brain stay BUSY.", n_at=18.2, narr_y=1530),
    dict(id="energy", s=25.0, e=32.0, bg="night", clock="SMALL BUT HUNGRY", props=energy_props,
         narr="Just 2% of your BODY WEIGHT, but it burns about 20% of your ENERGY.", n_at=25.2,
         narr_y=1530),
    dict(id="bulb", s=32.0, e=39.0, bg="night", clock="POWER CHECK", props=bulb_props,
         narr="About 20 WATTS, like a dim BULB that never switches off.", n_at=32.2, narr_y=1530),
    dict(id="neurons", s=39.0, e=46.0, bg="night", clock="HEAD COUNT", props=neuron_props,
         narr="About 86 BILLION neurons, but only SOME fire at any moment.", n_at=39.2,
         narr_y=1530),
    dict(id="burst", s=46.0, e=TW, bg="night", clock="100% AT ONCE?", props=burst_props, overlay=burst_overlay,
         narr="Lots of neurons firing in one sudden burst? That's a SEIZURE, not a SUPERPOWER.",
         n_at=46.2, narr_y=1530),
    dict(id="twist", s=TW, e=60.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: the brain has NO PAIN SENSORS, so some brain surgery is done AWAKE!",
         n_at=TW + 0.2, narr_y=1530, say="I'm AWAKE?!", say_at=TW + 3.4, pitch=620),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        r = max(2, int(170 * p))
        brain(d, 540, 1290, r, lit=(0, 1, 2, 3, 4, 5) if int(T * 4) % 2 else (1,))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU USED", WHITE)], 130), 690, 0.75, "right"),
        (title([("100% OF YOUR", YEL)], 120), 830, 1.05, "left"),
        (title([("BRAIN?", YEL)], 150), 980, 1.35, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which fact shocked ", WHITE), ("YOU", YEL)], 84), 470, 0.15),
                      (title([("the most?", WHITE)], 96), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("cat", 1), ("dog", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=46.2, dur=6.5, g=0.05), dict(t0=TW, dur=7.0, g=0.08)],
    fx=[("ding", 7.0, 0.2), ("click", 11.6, 0.2), ("click", 12.3, 0.2), ("click", 13.0, 0.2),
        ("click", 13.7, 0.2), ("click", 14.4, 0.2), ("ding", 15.8, 0.25), ("pop", 25.8, 0.3),
        ("pop", 27.8, 0.3), ("click", 33.0, 0.3), ("tick", 40.0, 0.2), ("tick", 41.0, 0.2),
        ("crash", 47.2, 0.15), ("pop", TW + 1.0, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_used_100_percent_of_your_brain")
