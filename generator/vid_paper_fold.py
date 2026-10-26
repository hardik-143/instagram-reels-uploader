#!/usr/bin/env python3
"""What if you folded a sheet of paper 103 times? Thickness doubles each fold: 0.1 mm x 2^n (Scientific American).
7 folds ~1.3 cm; 17 folds ~13 m; 20 folds ~105 m vs Qutub Minar 72.5 m (UNESCO); 27 folds ~13.4 km, above
Everest (8,849 m) and cruising jets; 41 folds ~220,000 km (halfway to the Moon), 42 folds ~440,000 km vs Moon
~384,000 km (SciAm); 51 folds ~225 million km vs Sun 150 million km (SciAm); 83 folds ~102,000 light-years vs Milky
Way ~100,000 ly (NASA via Universe Today); 103 folds ~107 billion ly vs observable universe ~93 billion ly (SciAm).
Twist: the famous real record is 12 folds, by a high-school student using a ~1,200 m strip (SciAm)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

PAPER = (252, 252, 246)
LINE = (190, 200, 220)
_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=60, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def stack(d, cx, base, h, w=130, lines=10):
    """Paper stack standing on `base`, height h px."""
    h = max(6, h)
    d.rectangle([cx - w / 2, base - h, cx + w / 2, base], fill=PAPER, outline=OUTL, width=5)
    n = max(1, min(lines, int(h / 14)))
    for k in range(1, n):
        y = base - h * k / n
        d.line([(cx - w / 2 + 6, y), (cx + w / 2 - 6, y)], fill=LINE, width=3)

def grow(sc, T, dur=1.6):
    return ease_out(clamp((T - sc["s"] - 0.3) / dur))

# ------------------------------------------------------------------ scenes
def sheet_props(frame, d, T, sc):
    p = grow(sc, T)
    d.rectangle([0, 1330, W, H], fill=(150, 110, 80))
    d.rectangle([560, 1250, 1040, 1330], fill=(200, 150, 100), outline=OUTL, width=6)  # desk top
    stack(d, 800, 1250, 6 + 70 * p, 220, 7)
    put_label(frame, "0.1 MM", 800, 1100, 60, WHITE)
    if p > 0.5: put_label(frame, "7 FOLDS = 1.3 CM", 800, 1170, 52)

def house_props(frame, d, T, sc):
    p = grow(sc, T)
    for k in range(4):   # 4-storey building on the right
        y = 1330 - (k + 1) * 105
        d.rectangle([560, y, 760, y + 105], fill=(250, 180, 140), outline=OUTL, width=5)
        d.rectangle([600, y + 25, 650, y + 75], fill=(180, 220, 250), outline=OUTL, width=4)
        d.rectangle([680, y + 25, 730, y + 75], fill=(180, 220, 250), outline=OUTL, width=4)
    stack(d, 870, 1330, 470 * p, 120)
    put_label(frame, "13 METRES", 880, 790, 56)

def qutub(d, cx, base, h):
    w0, w1 = 120, 40
    d.polygon([(cx - w0 / 2, base), (cx - w1 / 2, base - h), (cx + w1 / 2, base - h), (cx + w0 / 2, base)],
              fill=(200, 110, 80), outline=OUTL)
    for k in range(1, 5):
        y = base - h * k / 5
        ww = w0 + (w1 - w0) * k / 5
        d.rectangle([cx - ww / 2 - 10, y - 8, cx + ww / 2 + 10, y + 8], fill=(170, 90, 70), outline=OUTL, width=3)

def qutub_props(frame, d, T, sc):
    p = grow(sc, T)
    qutub(d, 640, 1330, 330)
    put_label(frame, "72.5 M", 640, 940, 44, WHITE)
    stack(d, 880, 1330, 470 * p, 110)
    if p > 0.4: put_label(frame, "105 M", 900, 800, 48, YEL)

def plane(d, x, y, s=1.0):
    d.ellipse([x - 90 * s, y - 18 * s, x + 90 * s, y + 18 * s], fill=WHITE, outline=OUTL, width=4)
    d.polygon([(x - 10 * s, y), (x + 30 * s, y), (x - 30 * s, y + 60 * s), (x - 60 * s, y + 60 * s)],
              fill=(220, 225, 235), outline=OUTL)
    d.polygon([(x - 90 * s, y), (x - 60 * s, y), (x - 95 * s, y - 45 * s), (x - 110 * s, y - 45 * s)],
              fill=(220, 225, 235), outline=OUTL)

def everest_props(frame, d, T, sc):
    p = grow(sc, T)
    lt = T - sc["s"]
    d.polygon([(420, 1330), (700, 960), (980, 1330)], fill=(120, 120, 140), outline=OUTL)
    d.polygon([(650, 1026), (700, 960), (750, 1026), (720, 1010), (700, 1030), (680, 1010)], fill=WHITE, outline=OUTL)
    put_label(frame, "EVEREST 8.8 KM", 700, 1250, 40, WHITE)
    plane(d, 640 + 60 * math.sin(lt * 0.8), 880, 0.8)
    stack(d, 930, 1330, 560 * p, 60, 14)
    if p > 0.5: put_label(frame, "13 KM", 930, 800, 52)

def earth_moon(frame, d, T, sc, far=False):
    lt = T - sc["s"]
    comp(frame, draw_char("earth", 260, T, 0, E.blink_at(T, 0.2), (0.3, -0.3), lt * 0.3), 560, 1080)

def moon_props(frame, d, T, sc):
    lt = T - sc["s"]
    earth_moon(frame, d, T, sc)
    comp(frame, draw_char("moon", 180, T, 0, E.blink_at(T, 0.7), (-0.3, 0.4)), 600, 820)
    # line rising from Earth: halfway at 41 folds, past the Moon at 42
    x = 690
    full = 1100 - 910
    if lt < 3.0:
        h = full * 0.5 * ease_out(clamp((lt - 0.3) / 1.2))
        lab = "FOLD 41"
    else:
        h = full * 0.5 + full * 0.75 * ease_out(clamp((lt - 3.0) / 0.8))
        lab = "FOLD 42"
    d.rectangle([x - 9, 1100 - h, x + 9, 1100], fill=PAPER, outline=OUTL, width=3)
    put_label(frame, lab, 900, 1150, 48)

def sun_props(frame, d, T, sc):
    p = grow(sc, T, 2.0)
    comp(frame, draw_char("earth", 150, T, 0, False, (0.4, -0.3), T * 0.3), 560, 1170)
    x0, y0, x1, y1 = 650, 1175, 880, 870
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    d.line([(x0, y0), (xe, ye)], fill=OUTL, width=18)
    d.line([(x0, y0), (xe, ye)], fill=PAPER, width=10)
    put_label(frame, "22 CRORE KM", 860, 1200, 48)

def galaxy(d, cx, cy, r, rot):
    for arm in range(2):
        pts = []
        for i in range(60):
            t = i / 59
            a = rot + arm * math.pi + t * 4.2
            rr = r * t
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.45))
        d.line(pts, fill=(200, 190, 255), width=16)
        d.line(pts, fill=(255, 250, 230), width=6)
    d.ellipse([cx - 50, cy - 25, cx + 50, cy + 25], fill=(255, 240, 200), outline=OUTL, width=3)

def galaxy_props(frame, d, T, sc):
    p = grow(sc, T)
    lt = T - sc["s"]
    galaxy(d, 700, 1060, 320, lt * 0.2)
    d.rectangle([380, 1060 - 9, 380 + 640 * p, 1060 + 9], fill=PAPER, outline=OUTL, width=3)
    put_label(frame, "1 LAKH LIGHT-YEARS", 700, 1230, 46)

def universe_props(frame, d, T, sc):
    p = grow(sc, T, 2.0)
    lt = T - sc["s"]
    cx, cy, r = 690, 1030, 220
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 30, 90), outline=(180, 160, 255), width=6)
    for k in range(70):
        a = k * 2.39996; rr = r * math.sqrt(((k * 37) % 100) / 100.0) * 0.92
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        s = 3 + (k % 3) * 2
        d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 240, 210))
    w = 2 * r * 1.15 * p
    x0 = cx - r * 1.15
    d.rectangle([x0, cy - 12, x0 + w, cy + 12], fill=PAPER, outline=OUTL, width=3)
    put_label(frame, "93 BILLION LIGHT-YEARS", 640, 1270, 42)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp(lt / 1.4))
    # a long strip of paper unrolling along the floor
    d.rectangle([440, 1250, 440 + 600 * p, 1300], fill=PAPER, outline=OUTL, width=4)
    for k in range(int(12 * p)):
        x = 470 + k * 48
        d.line([(x, 1255), (x, 1295)], fill=LINE, width=3)
    put_label(frame, "RECORD: 12 FOLDS", 740, 1000, 58)
    if lt > 1.5: put_label(frame, "1.2 KM OF PAPER", 740, 1090, 52, WHITE)

def notebook_intro(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        stack(d, 540, 1520, 60 + 160 * p * (0.5 + 0.5 * abs(math.sin(T * 3))), 260 * max(p, 0.1), 8)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="sheet", s=4.0, e=10.5, bg="living", clock="FOLD 7", char="kid", pos=(250, 1110, 400),
         props=sheet_props, look=(0.6, 0.2),
         narr="One page is just 0.1 MM thick. Fold it 7 times: about 1 CM.", n_at=4.2,
         say="Easy PEASY!", say_at=6.6, pitch=600),
    dict(id="house", s=10.5, e=17.0, bg="gully", clock="FOLD 17", char="kid", pos=(250, 1130, 380),
         props=house_props, look=(0.6, -0.2),
         narr="Every fold DOUBLES it. Fold 17: 13 METRES, taller than a 4-storey building.", n_at=10.7,
         say="Wait, WHAT?", say_at=13.4, pitch=620),
    dict(id="qutub", s=17.0, e=23.5, bg="day", clock="FOLD 20", char="uncle", pos=(240, 1130, 380),
         props=qutub_props, look=(0.6, -0.3),
         narr="Fold 20: 105 METRES. Taller than the QUTUB MINAR.", n_at=17.2,
         say="Bas karo, BETA!", say_at=19.6, pitch=300),
    dict(id="everest", s=23.5, e=30.0, bg="speed", clock="FOLD 27", char="kid", pos=(230, 1150, 340),
         props=everest_props, look=(0.6, -0.4),
         narr="Fold 27: 13 KM. Above EVEREST. Above the PLANES.", n_at=23.7,
         say="Hello, PILOT!", say_at=26.0, pitch=620),
    dict(id="moon", s=30.0, e=37.0, bg="space", clock="FOLD 41-42", char="kid", pos=(240, 1150, 320),
         props=moon_props, look=(0.6, -0.4),
         narr="Fold 41: HALFWAY to the Moon. Just ONE more fold: PAST it!", n_at=30.2,
         say="One fold did HALF the work!", say_at=33.3, pitch=620),
    dict(id="sun", s=37.0, e=43.5, bg="space", clock="FOLD 51", char="sun", pos=(800, 960, 300),
         props=sun_props, look=(-0.6, 0.3),
         narr="Fold 51: about 22 CRORE KM. PAST the SUN.", n_at=37.2,
         say="Paper? HERE?!", say_at=39.4, pitch=420),
    dict(id="galaxy", s=43.5, e=50.0, bg="night", clock="FOLD 83", props=galaxy_props,
         narr="Fold 83: about 1 LAKH light-years. Across our whole MILKY WAY.", n_at=43.7),
    dict(id="universe", s=50.0, e=57.0, bg="space", clock="FOLD 103", char="kid", pos=(230, 1170, 300),
         props=universe_props, look=(0.6, -0.2),
         narr="Fold 103: WIDER than the observable UNIVERSE. All from ONE page.", n_at=50.2,
         say="I broke the UNIVERSE!", say_at=53.0, pitch=620),
    dict(id="twist", s=57.0, e=64.5, bg="twist", clock="REAL LIFE", char="kid", state="puff",
         pos=(250, 1120, 380), props=twist_props, twist=True, look=(0.6, 0.2),
         narr="Reality: each fold needs WAY more paper. The record is 12 FOLDS.", n_at=57.2,
         say="With a 1.2 KM strip!", say_at=60.4, pitch=600),
    dict(id="outro", s=64.5, e=69.5),
]

cfg = dict(
    total=69.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("you folded", WHITE)], 120), 770, 0.75, "right"),
        (title([("PAPER", YEL)], 170), 920, 1.05, "left"),
        (title([("103 TIMES?", YEL)], 130), 1080, 1.5, "pop"),
    ], extra=notebook_intro),
    outro=dict(lines=[(title([("How many folds", WHITE)], 88), 470, 0.15),
                      (title([("can", WHITE), (" YOU", YEL), (" do?", WHITE)], 92), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("moon", 1), ("sun", 1), ("earth", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=56.85), dict(t0=64.5, t1=69.5, melody=True)],
    drones=[dict(t0=43.5, dur=6.5, g=0.06), dict(t0=57.0, dur=7.5, g=0.08)],
    fx=[("pop", 4.6, 0.6), ("pop", 5.0, 0.6), ("pop", 5.4, 0.6), ("pop", 5.8, 0.6),
        ("whoosh", 10.9, 0.6), ("rumble", 17.4, 0.4, dict(dd=2.0)), ("wind", 23.8, 0.4, dict(dd=5.0)),
        ("whoosh", 33.0, 0.8), ("boom", 37.4, 0.7), ("boom", 50.4, 1.0)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_paper_fold")
