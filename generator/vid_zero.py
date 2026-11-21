#!/usr/bin/env python3
"""What if zero was never invented? Facts: Roman numerals have no zero and no place value (2026 = MMXXVI).
Babylonians (c. 1700-400 BC) marked empty places with a gap/placeholder, not a number (MacTutor 'A history of Zero').
Brahmagupta's Brahmasphutasiddhanta, 628 CE, gave rules for zero as a number: a number minus itself is zero, a number
times zero is zero (MacTutor, Brahmagupta biography). Gwalior Chaturbhuj temple inscription, 876 CE, records a garden
of 187 x 270 hastas; the 0 in 270 is the earliest known circular zero in stone (MacTutor; Wikipedia 'Chaturbhuj
Temple, Gwalior'). Word chain: Sanskrit shunya ('empty') -> Arabic sifr -> Latin zephirum (Fibonacci, Liber Abaci
1202) -> Italian zero (MacTutor 'Earliest uses of mathematical words'; Etymonline). Computers use binary 0 and 1.
Cricket 'duck' = out for 0, short for 'duck's egg' from its 0-like shape, recorded 1866 (Wikipedia 'Duck (cricket)').
Twist: the AD/BC calendar has no year zero, 1 BC is followed by AD 1 (Wikipedia 'Year zero'). The Bakhshali
manuscript was deliberately left out: Oxford's 2017 3rd-4th century dating was revised in 2024 to c. 9th-11th c."""
import math
import numpy as np
from PIL import Image
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
STONE, STONE_D = (176, 160, 140), (120, 105, 90)
LEAF, LEAF_D = (222, 190, 120), (170, 135, 70)
RED = (255, 120, 80)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def big_zero(d, cx, cy, r, col=YEL, w=None):
    w = w or max(6, int(r * 0.32))
    d.ellipse([cx - 0.72 * r, cy - r, cx + 0.72 * r, cy + r], outline=OUTL, width=w + 12)
    d.ellipse([cx - 0.72 * r + 6, cy - r + 6, cx + 0.72 * r - 6, cy + r - 6], outline=col, width=w)

# ---------------------------------------------------------------- props
def roman_props(frame, d, T, sc):
    lt = T - sc["s"]
    lab_at(frame, "2026", 540, 620, WHITE, 170)
    if lt > 1.2:
        d.line([(330, 620), (750, 620)], fill=RED, width=16)
    if lt > 2.0:
        p = min(ease_back(clamp((lt - 2.0) / 0.5)), 1.1)
        if p > 0.05:
            lab_at(frame, "MMXXVI", 540, 900, YEL, max(10, int(170 * p)))
    if lt > 3.6:
        mini(frame, "uncle", 540, 1230, 240, T, 1, (0, -0.4))

def gap_props(frame, d, T, sc):
    lt = T - sc["s"]
    # two number tiles with a suspicious space
    for x in (360, 720):
        d.rounded_rectangle([x - 110, 560, x + 110, 820], radius=24, fill=(60, 50, 90), outline=OUTL, width=7)
        lab_at(frame, "1", x, 690, WHITE, 180)
    if lt > 1.2:
        lab_at(frame, "?", 540, 690, RED, 150)
    opts = ["11?", "101?", "110?"]
    for i, o in enumerate(opts):
        if lt > 2.0 + 0.5 * i:
            lab_at(frame, o, 220 + 320 * i, 970, YEL, 90)
    if lt > 4.0:
        lab_at(frame, "BABYLON: LEAVE A GAP", 540, 1200, WHITE, 60)

def leaf(d, x0, y0, x1, y1):
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=LEAF, outline=OUTL, width=8)
    for y in range(y0 + 40, y1 - 20, 46):
        d.line([(x0 + 40, y), (x1 - 40, y)], fill=LEAF_D, width=3)
    d.ellipse([x0 + 60 - 14, (y0 + y1) / 2 - 14, x0 + 60 + 14, (y0 + y1) / 2 + 14], fill=LEAF_D)
    d.ellipse([x1 - 60 - 14, (y0 + y1) / 2 - 14, x1 - 60 + 14, (y0 + y1) / 2 + 14], fill=LEAF_D)

def brahma_props(frame, d, T, sc):
    lt = T - sc["s"]
    lab_at(frame, "628 CE", 540, 470, YEL, 96)
    leaf(d, 110, 620, 970, 1180)
    rules = ["5 - 5 = 0", "5 x 0 = 0", "5 + 0 = 5"]
    for i, r in enumerate(rules):
        if lt > 1.0 + 0.9 * i:
            lab_at(frame, r, 540, 740 + 160 * i, WHITE, 96)
    if lt > 4.2:
        lab_at(frame, "ZERO = A NUMBER", 540, 1290, YEL, 66)

def gwalior_props(frame, d, T, sc):
    lt = T - sc["s"]
    # temple silhouette
    d.polygon([(540, 470), (700, 760), (380, 760)], fill=STONE_D, outline=OUTL)
    d.rectangle([380, 760, 700, 820], fill=STONE_D, outline=OUTL, width=6)
    # carved slab
    d.rounded_rectangle([170, 860, 910, 1240], radius=20, fill=STONE, outline=OUTL, width=8)
    for k in range(6):
        d.line([(210, 900 + 55 * k), (870, 900 + 55 * k)], fill=STONE_D, width=4)
    if lt > 1.0:
        p = min(ease_back(clamp((lt - 1.0) / 0.5)), 1.1)
        if p > 0.05:
            l = label("270", max(10, int(220 * p)), (90, 70, 55))
            comp(frame, l, 540 - l.width / 2, 1050 - l.height / 2)
    if lt > 2.2:
        a = 0.5 + 0.5 * math.sin(T * 6)
        d.ellipse([600, 940, 760, 1160], outline=(255, int(200 + 55 * a), 60), width=10)
    if lt > 3.0:
        lab_at(frame, "876 CE, IN STONE", 540, 1310, YEL, 64)

def journey_props(frame, d, T, sc):
    lt = T - sc["s"]
    words = [("SHUNYA", "SANSKRIT"), ("SIFR", "ARABIC"), ("ZEPHIRUM", "LATIN"), ("ZERO", "ITALIAN")]
    for i, (w, lang) in enumerate(words):
        t0 = 0.6 + 1.1 * i
        if lt > t0:
            y = 520 + 210 * i
            p = min(ease_back(clamp((lt - t0) / 0.45)), 1.1)
            if p > 0.05:
                lab_at(frame, w, 540, y, YEL if i in (0, 3) else WHITE, max(10, int(92 * p)))
            lab_at(frame, lang, 540, y + 70, (190, 190, 220), 40)
            if i < 3 and lt > t0 + 0.6:
                d.polygon([(520, y + 120), (560, y + 120), (540, y + 150)], fill=WHITE, outline=OUTL)

rng = np.random.default_rng(3)
BITS = [(int(x), float(sp), int(ph)) for x, sp, ph in zip(np.linspace(130, 950, 12), rng.uniform(120, 260, 12),
                                                            rng.integers(0, 2, 12))]
def binary_props(frame, d, T, sc):
    lt = T - sc["s"]
    for j, (x, sp, ph) in enumerate(BITS):
        for k in range(6):
            y = 440 + ((lt * sp + k * 130 + j * 37) % 760)
            ch = "0" if (k + ph + int(T * 2)) % 2 else "1"
            lab_at(frame, ch, x, y, (90, 220, 140), 50)
    # phone
    d.rounded_rectangle([370, 640, 710, 1240], radius=50, fill=(30, 30, 40), outline=OUTL, width=10)
    d.rounded_rectangle([395, 690, 685, 1180], radius=20, fill=(40, 70, 120))
    if lt > 1.2:
        lab_at(frame, "0101", 540, 860, YEL, 90)
        lab_at(frame, "1100", 540, 980, WHITE, 90)
    if lt > 3.4:
        lab_at(frame, "ALL 0s AND 1s", 540, 1310, YEL, 66)

def duck_props(frame, d, T, sc):
    lt = T - sc["s"]
    # scoreboard
    d.rounded_rectangle([200, 470, 880, 700], radius=24, fill=(30, 50, 40), outline=OUTL, width=8)
    lab_at(frame, "RUNS:", 400, 585, WHITE, 76)
    big_zero(d, 690, 585, 80, YEL, 18)
    if lt > 1.6:
        p = min(ease_back(clamp((lt - 1.6) / 0.5)), 1.1)
        r = max(4, 150 * p)
        d.ellipse([540 - 0.75 * r, 1000 - r, 540 + 0.75 * r, 1000 + r], fill=(250, 248, 236), outline=OUTL, width=8)
    if lt > 2.4:
        lab_at(frame, "DUCK'S EGG", 540, 1230, YEL, 72)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    y = 1000
    d.line([(60, y), (1020, y)], fill=WHITE, width=10)
    ticks = [(150, "2 BC"), (360, "1 BC"), (720, "AD 1"), (930, "AD 2")]
    for i, (x, t) in enumerate(ticks):
        if lt > 0.4 + 0.3 * i:
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=YEL, outline=OUTL, width=5)
            lab_at(frame, t, x, y + 90, WHITE, 56)
    if lt > 1.8:
        big_zero(d, 540, y - 10, 80, (110, 110, 140), 16)
        d.line([(470, y - 90), (610, y + 70)], fill=RED, width=18)
        d.line([(610, y - 90), (470, y + 70)], fill=RED, width=18)
    if lt > 2.6:
        lab_at(frame, "NO YEAR ZERO", 540, 1260, YEL, 84)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="roman", s=4.0, e=11.0, bg="night", clock="NO ZERO", props=roman_props,
         narr="No ZERO? Then 2026 looks like the Romans wrote it: MMXXVI.", n_at=4.2, narr_y=1530),
    dict(id="gap", s=11.0, e=18.0, bg="night", clock="SPOT THE GAP", props=gap_props,
         narr="And how do you tell 11 from 101? Babylonians just left a GAP.", n_at=11.2, narr_y=1530),
    dict(id="brahma", s=18.0, e=25.0, bg="night", clock="INDIA, 628 CE", props=brahma_props,
         narr="Then in India, BRAHMAGUPTA wrote RULES for zero as a real NUMBER.", n_at=18.2, narr_y=1530),
    dict(id="gwalior", s=25.0, e=32.0, bg="night", clock="GWALIOR", props=gwalior_props,
         narr="A GWALIOR temple slab from 876 CE has a ZERO carved in the number 270.", n_at=25.2,
         narr_y=1530),
    dict(id="journey", s=32.0, e=39.0, bg="night", clock="ZERO TRAVELS", props=journey_props,
         narr="SHUNYA became Arabic SIFR, Latin ZEPHIRUM, and finally ZERO.", n_at=32.2, narr_y=1530),
    dict(id="binary", s=39.0, e=46.0, bg="night", clock="NO ZERO, NO...", props=binary_props,
         narr="No zero, no BINARY. Your phone runs on billions of 0s and 1s.", n_at=39.2, narr_y=1530),
    dict(id="duck", s=46.0, e=TW, bg="stadium", clock="OUT FOR 0", props=duck_props,
         narr="Even cricket's DUCK, out for ZERO, comes from a 'duck's EGG' shape.", n_at=46.2, narr_y=1530),
    dict(id="twist", s=TW, e=60.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: our calendar has NO YEAR ZERO. 1 BC jumps straight to AD 1!",
         n_at=TW + 0.2, narr_y=1530, say="Where did it GO?!", say_at=TW + 3.4, pitch=620),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        big_zero(d, 540, 1300, max(30, 150 * p), YEL, 30)
        if T > 2.8:
            d.line([(420, 1170), (660, 1430)], fill=RED, width=22)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("ZERO WAS", WHITE)], 130), 690, 0.75, "right"),
        (title([("NEVER", YEL)], 150), 830, 1.05, "left"),
        (title([("INVENTED?", YEL)], 140), 990, 1.35, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which fact surprised ", WHITE), ("YOU", YEL)], 80), 470, 0.15),
                      (title([("the most?", WHITE)], 96), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("cat", 1), ("dog", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, drums=True, clap=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.08)],
    fx=[("crash", 5.2, 0.12), ("pop", 6.1, 0.3), ("pop", 12.2, 0.25), ("pop", 13.0, 0.2), ("pop", 13.5, 0.2),
        ("pop", 14.0, 0.2), ("ding", 19.0, 0.2), ("ding", 19.9, 0.2), ("ding", 20.8, 0.2), ("pop", 26.0, 0.3),
        ("pop", 32.6, 0.25), ("pop", 33.7, 0.25), ("pop", 34.8, 0.25), ("ding", 35.9, 0.3),
        ("click", 40.2, 0.2), ("click", 40.6, 0.2), ("cheer", 46.6, 0.12), ("pop", 47.6, 0.3),
        ("pop", TW + 1.8, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_zero_was_never_invented")
