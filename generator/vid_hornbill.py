#!/usr/bin/env python3
"""What if you were a hornbill for a day? Facts (great hornbill, Buceros bicornis): 95-130 cm long, ~152 cm wingspan,
2-4 kg, males ~3 kg (Wikipedia; ADW: avg 3 kg, wingspan 151-178 cm). State bird of Kerala and Arunachal Pradesh
(Wikipedia list of Indian state birds). Casque on top of the bill is hollow (Wikipedia, ADW); males butt casques,
including in flight (Wikipedia, ADW). Wingbeats can be heard from a distance, like a steam locomotive starting up
(Wikipedia; Nature inFocus: almost a kilometre). Mainly fruit-eaters, figs most important (Wikipedia, ADW); 'obtain
water entirely from their diet of fruits' (Wikipedia). Disperse large seeds (ADW: Myristica), 'farmers of the
forest' (Mongabay-India, Jul 2026). Female seals herself into a tree cavity, fed by the male through a slit, and
moults completely (Wikipedia, ADW); stays sealed ~3-4 months (Nature inFocus, PBS 'three months'). India has nine
hornbill species (Mongabay-India; Nature inFocus). Hornbill Festival, Kisama Heritage Village near Kohima, Nagaland,
1-10 Dec 2026, named after the hornbill (Time Out India, Sep 2026). IUCN Vulnerable (Wikipedia, Mongabay).
Twist: the seal is 'a plaster made up mainly of feces' (Wikipedia; ADW: her own and her mate's feces)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad, paste_c

TW = 60.0
BLK, CREAM, BILL, BILL_D = (34, 34, 40), (248, 236, 190), (255, 200, 40), (230, 150, 30)
RED = (255, 110, 90)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col); comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def hornbill(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    """Side-view cartoon great hornbill facing right. state: 1 = perched, "fly" = flapping."""
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))
    def EL(b, fill, w=2.6):
        d.ellipse([v * u for v in b], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    def PG(pts, fill, w=2.6):
        d.polygon([(x * u, y * u) for x, y in pts], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    def LN(pts, w=2.6, fill=OUTL):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")
    fly = state == "fly"
    # tail: white with a black band
    if fly:
        PG([(52, 104), (6, 112), (6, 132), (52, 118)], WHITE)
        PG([(22, 110), (14, 111), (14, 130), (22, 128)], BLK, w=0)
    else:
        PG([(56, 118), (30, 186), (52, 192), (72, 126)], WHITE)
        PG([(38, 166), (34, 176), (56, 182), (60, 172)], BLK, w=0)
    # legs
    if not fly:
        for x in (88, 104):
            LN([(x, 136), (x - 2, 158)], 5, (90, 90, 100))
            LN([(x - 10, 160), (x + 8, 160)], 4, (90, 90, 100))
    # body
    EL((46, 82, 132, 146), BLK)
    EL((86, 112, 130, 144), WHITE, w=0)   # white belly
    # wing
    if fly:
        a = math.sin(T * 9)
        tip_y = 40 + 80 * (0.5 - 0.5 * a)
        PG([(64, 96), (112, 96), (96, tip_y), (52, tip_y - 6)], BLK)
        PG([(70, 96), (104, 96), (92, (96 + tip_y) / 2), (62, (96 + tip_y) / 2 - 3)], WHITE, w=0)
        LN([(64, 96), (112, 96)], 2.6)
    else:
        EL((54, 88, 118, 128), BLK)
        PG([(60, 112), (114, 104), (112, 114), (62, 122)], WHITE, w=0)   # white wing bar
    # neck + head (creamy yellow)
    PG([(108, 104), (122, 62), (146, 62), (134, 108)], CREAM, w=0)
    EL((116, 40, 160, 84), CREAM)
    # bill (curved down) with talk gap
    gap = 6 * talk
    PG([(150, 58), (198, 82 + gap), (190, 92 + gap), (148, 74)], BILL)                     # lower
    PG([(148, 50), (186, 60), (199, 80), (150, 66)], BILL)                                # upper
    # casque on top
    PG([(136, 40), (176, 44), (190, 58), (150, 54)], BILL)
    PG([(176, 44), (190, 58), (184, 56), (172, 46)], BLK, w=0)
    LN([(146, 52), (178, 52)], 1.8, BILL_D)
    # black face mask + red eye
    EL((132, 52, 152, 72), BLK, w=0)
    ex, ey = 141, 61
    if blink:
        d.arc([(ex - 6) * u, (ey - 4) * u, (ex + 6) * u, (ey + 4) * u], 200, 340, fill=WHITE, width=lw(2.4))
    else:
        EL((ex - 6.5, ey - 6.5, ex + 6.5, ey + 6.5), (210, 40, 40), w=1.8)
        px, py = ex + 1 + look[0] * 2, ey + look[1] * 2
        EL((px - 3, py - 3, px + 3, py + 3), (20, 10, 10), w=0)
        EL((px - 2.2, py - 2.6, px - 0.4, py - 0.8), WHITE, w=0)
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "hornbill":
        return hornbill(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0, flip=False):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    if flip: spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def forest(kind="day", branch=True):
    k = (kind, branch)
    if k in _bgc: return _bgc[k]
    sky = {"day": [(0, (150, 214, 200)), (0.7, (214, 240, 200)), (1, (214, 240, 200))],
           "dawn": [(0, (120, 120, 200)), (0.5, (255, 170, 140)), (1, (255, 220, 160))]}[kind]
    img = grad(sky, W, H); d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    # distant hills
    d.polygon([(0, 1000), (260, 880), (520, 960), (800, 860), (1080, 940), (1080, H), (0, H)], fill=(90, 150, 110))
    # tree trunks + canopy
    for x in (90, 330, 760, 990):
        d.rectangle([x - 26, 600, x + 26, H], fill=(96, 70, 52))
    for _ in range(26):
        x, y, r = rng.uniform(-40, W + 40), rng.uniform(480, 760), rng.uniform(80, 150)
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(54, 120, 70) if rng.random() < 0.5 else (70, 140, 80))
    d.rectangle([0, 1380, W, H], fill=(60, 100, 60))
    if branch:
        d.line([(-20, 1250), (420, 1236), (1100, 1262)], fill=(110, 76, 50), width=34)
        d.ellipse([880, 1196, 990, 1260], fill=(70, 140, 80))
    _bgc[k] = img
    return img

def bg_day(T): return forest("day")
def bg_dawn(T): return forest("dawn")
def bg_open(T): return forest("day", False)

PERCH = (540, 1050, 520)

# ---------------------------------------------------------------- props
def wake_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.8: top_label(frame, "GREAT HORNBILL", 400, YEL, 84)
    if lt > 2.4: lab_at(frame, "ABOUT 3 KG", 300, 620, WHITE, 56)
    if lt > 3.6: lab_at(frame, "WINGS ~1.5 M", 780, 620, WHITE, 56)

def state_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "STATE BIRD OF", 400, WHITE, 70)
    if lt > 1.0: paste_c(frame, label("KERALA", 76, YEL), 540, 560, 0.3 + 0.7 * ease_back(clamp((lt - 1.0) / 0.35)))
    if lt > 2.4: paste_c(frame, label("ARUNACHAL PRADESH", 66, YEL), 540, 665,
                         0.3 + 0.7 * ease_back(clamp((lt - 2.4) / 0.35)))

def casque_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "THE CASQUE", 400, YEL, 84)
    if lt > 1.2:
        # pointer line to the casque on the bird (bird at 540,1050 size 520: casque ~ (640, 830))
        d.line([(780, 650), (712, 896)], fill=WHITE, width=8)
        d.ellipse([698, 892, 724, 918], fill=WHITE, outline=OUTL, width=4)
        lab_at(frame, "HOLLOW!", 800, 600, YEL, 66)

def casque_after(frame, d, T, sc):
    pass

def fly_pos(T):
    return (540 + 60 * math.sin(T * 1.2), 960 + 30 * math.sin(T * 2.4), 560)

def flight_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.8: top_label(frame, "WHOOSH... WHOOSH...", 400, WHITE, 70)
    if lt > 2.6: lab_at(frame, "LIKE A STEAM TRAIN", 540, 560, YEL, 62)
    # wind puffs
    for k in range(4):
        x = 1100 - ((lt * 500 + k * 300) % 1300)
        y = 700 + k * 90
        d.ellipse([x - 50, y - 18, x + 50, y + 18], fill=(255, 255, 255, 160))

def fig(d, x, y, r=26):
    d.ellipse([x - r, y - r, x + r, y + r * 1.1], fill=(150, 70, 120), outline=OUTL, width=4)
    d.line([(x, y - r), (x + 4, y - r - 12)], fill=(70, 110, 50), width=5)

def figs_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "MENU: FIGS, FIGS, FIGS", 400, YEL, 64)
    for i in range(6):
        if lt > 0.5 + i * 0.3:
            fig(d, 200 + i * 136, 560 + 20 * math.sin(T * 3 + i))
    if lt > 3.8:
        d.rounded_rectangle([250, 660, 830, 760], radius=30, fill=(40, 30, 60), outline=OUTL, width=6)
        lab_at(frame, "WATER: FROM FRUIT", 540, 710, WHITE, 54)

def farmer_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "FARMER OF THE FOREST", 400, YEL, 66)
    # seeds dropping and sprouting on the ground
    for i, x in enumerate((180, 420, 680, 900)):
        t0 = 0.8 + i * 0.7
        if lt > t0:
            q = clamp((lt - t0) / 0.8)
            y = 700 + 640 * q
            if q < 1:
                d.ellipse([x - 14, y - 18, x + 14, y + 18], fill=(120, 80, 40), outline=OUTL, width=4)
            else:
                g = clamp((lt - t0 - 0.8) / 1.0)
                d.line([(x, 1360), (x, 1360 - 90 * g)], fill=(60, 150, 60), width=10)
                if g > 0.4:
                    d.ellipse([x - 40, 1340 - 90 * g, x, 1360 - 90 * g + 10], fill=(80, 180, 80), outline=OUTL, width=3)
                    d.ellipse([x, 1340 - 90 * g, x + 40, 1360 - 90 * g + 10], fill=(80, 180, 80), outline=OUTL, width=3)

def fly_across(T):
    return (1200 - ((T - 39.0) * 260) % 1500, 900, 380)

TX0, TX1, HOLE_Y = 330, 720, 860
def tree_with_nest(d, open_slit=True, poop=0.0):
    d.rectangle([TX0, 500, TX1, 1390], fill=(110, 78, 54), outline=OUTL, width=6)
    for k in range(6):
        y = 560 + k * 140
        d.arc([TX0 + 30, y, TX1 - 30, y + 60], 200, 340, fill=(90, 62, 44), width=6)
    # sealed hole
    col = tuple(int(a * (1 - poop) + b * poop) for a, b in zip((150, 112, 70), (150, 140, 100)))
    d.ellipse([440, HOLE_Y - 150, 610, HOLE_Y + 150], fill=col, outline=OUTL, width=6)
    if open_slit:
        d.rounded_rectangle([515, HOLE_Y - 90, 535, HOLE_Y + 90], radius=8, fill=(20, 16, 14))
        # mum's bill tip peeking through the slit
        d.polygon([(525, HOLE_Y - 20), (560, HOLE_Y), (525, HOLE_Y + 14)], fill=BILL, outline=OUTL)
    if poop > 0:
        rng = np.random.default_rng(11)
        for _ in range(int(22 * poop)):
            x, y = rng.uniform(460, 590), rng.uniform(HOLE_Y - 120, HOLE_Y + 120)
            d.ellipse([x - 9, y - 6, x + 9, y + 6], fill=(240, 240, 230))

def nest_props(frame, d, T, sc):
    lt = T - sc["s"]
    tree_with_nest(d)
    top_label(frame, "SEALED IN FOR MONTHS", 400, YEL, 66)
    if lt > 2.8:
        lab_at(frame, "FOOD SLIT", 170, HOLE_Y - 60, WHITE, 48)
        d.line([(170, HOLE_Y - 20), (505, HOLE_Y)], fill=WHITE, width=6)
    # dad perched beside the slit with a fig
    mini(frame, "hornbill", 830, HOLE_Y + 120, 330, T, 1, flip=True)
    if lt > 1.6: fig(d, 660, HOLE_Y + 10 + 6 * math.sin(T * 6), 22)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "INDIA: 9 HORNBILL SPECIES", 400, WHITE, 60)
    if lt > 2.2:
        d.rounded_rectangle([150, 560, 930, 760], radius=34, fill=(150, 40, 40), outline=OUTL, width=6)
        lab_at(frame, "HORNBILL FESTIVAL", 540, 620, YEL, 62)
        lab_at(frame, "NAGALAND · 1-10 DEC", 540, 705, WHITE, 50)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    tree_with_nest(d, True, clamp((lt - 1.2) / 1.5))
    if lt > 2.6:
        d.rounded_rectangle([190, 1170, 890, 1290], radius=30, fill=(40, 30, 60), outline=OUTL, width=6)
        lab_at(frame, "MOSTLY POOP!", 540, 1230, YEL, 70)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wake", s=4.0, e=11.0, bg_fn=bg_dawn, clock="6:00 AM", props=wake_props, char="hornbill", pos=PERCH,
         narr="You wake up as a GREAT HORNBILL: about 3 KG, with wings around 1.5 METRES wide.", n_at=4.2),
    dict(id="state", s=11.0, e=18.0, bg_fn=bg_day, clock="WHO ARE YOU?", props=state_props, char="hornbill",
         pos=PERCH, narr="You're the official STATE BIRD of KERALA and ARUNACHAL PRADESH.", n_at=11.2,
         say="Namaste!", say_at=15.4, pitch=420, bubble_y=840),
    dict(id="casque", s=18.0, e=25.0, bg_fn=bg_day, clock="YOUR HELMET", props=casque_props, char="hornbill",
         pos=PERCH, narr="That yellow HELMET on your beak is a CASQUE. Inside, it's HOLLOW.", n_at=18.2),
    dict(id="flight", s=25.0, e=32.0, bg_fn=bg_open, clock="TAKE OFF", props=flight_props, char="hornbill",
         state="fly", pos=fly_pos, narr="Your WINGBEATS whoosh like a STEAM TRAIN starting up.", n_at=25.2),
    dict(id="figs", s=32.0, e=39.0, bg_fn=bg_day, clock="BREAKFAST", props=figs_props, char="hornbill",
         pos=PERCH, narr="You eat mostly FIGS, and get all your WATER from fruit. No need to DRINK!", n_at=32.2),
    dict(id="farmer", s=39.0, e=46.0, bg_fn=bg_open, clock="YOUR JOB", props=farmer_props, char="hornbill",
         state="fly", pos=fly_across,
         narr="You swallow big SEEDS and drop them far away. New trees grow!", n_at=39.2),
    dict(id="nest", s=46.0, e=53.0, bg_fn=bg_open, clock="NEST TIME", props=nest_props,
         narr="Mum SEALS herself in a tree hole for MONTHS. Dad feeds her through a SLIT.", n_at=46.2),
    dict(id="india", s=53.0, e=TW, bg_fn=bg_day, clock="INDIA", props=india_props, char="hornbill", pos=PERCH,
         narr="India has 9 HORNBILL species. NAGALAND's big festival is named after YOU.", n_at=53.2),
    dict(id="twist", s=TW, e=67.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: that wall Mum builds? It's made MOSTLY of POOP!", n_at=TW + 0.2),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.7:
        x = 1300 - 760 * ease_out(clamp((T - 1.7) / 0.9))
        mini(frame, "hornbill", x, 1400, 440, T, "fly")

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU WERE A", WHITE)], 130), 690, 0.75, "right"),
        (title([("HORNBILL", YEL)], 180), 860, 1.05, "pop"),
        (title([("FOR A DAY?", WHITE)], 130), 1030, 1.4, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" stay", WHITE)], 96), 470, 0.15),
                      (title([("sealed in a tree?", WHITE)], 92), 600, 0.45)],
               row=[("hornbill", 1), ("pigeon", 1), ("kid", 1), ("cat", 1), ("hornbill", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.08)],
    fx=[("whoosh", 1.8, 0.4), ("pop", 13.0, 0.3), ("pop", 13.4, 0.3), ("ding", 19.4, 0.2),
        ("whoosh", 25.8, 0.45), ("whoosh", 26.9, 0.45), ("whoosh", 28.0, 0.45), ("pop", 32.8, 0.25),
        ("pop", 33.4, 0.25), ("pop", 34.0, 0.25), ("pop", 41.6, 0.2), ("pop", 42.3, 0.2),
        ("click", 47.8, 0.3), ("crowd", 55.4, 0.12), ("pop", TW + 2.8, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_were_a_hornbill")
