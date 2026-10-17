#!/usr/bin/env python3
"""What if you doubled one grain of rice on every chessboard square? (the old Indian chess legend)
Maths: square n holds 2^(n-1) grains; total 2^64 - 1. Grain mass ~20 mg (TNAU 1000-grain weights 20-24 g)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

RICE = (250, 246, 232)
_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=60, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def grain(d, x, y, r=9, ang=0.0):
    dx, dy = math.cos(ang) * r, math.sin(ang) * r
    d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=OUTL, width=int(r * 1.1) + 4)
    d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=RICE, width=int(r * 1.1))

def mound(d, cx, base, w, h, seed=0, n=0):
    d.chord([cx - w / 2, base - h, cx + w / 2, base + h], 180, 360, fill=RICE, outline=OUTL, width=6)
    for k in range(n):
        a = (k * 2.39996 + seed) % math.pi
        rr = ((k * 37) % 100) / 100.0
        x = cx + math.cos(a) * w / 2 * rr * 0.9
        y = base - math.sin(a) * h * rr * 0.9
        d.arc([x - 9, y - 4, x + 9, y + 4], 200, 340, fill=(200, 190, 170), width=3)

# ----------------------------------------------------------- palace background
_palace = None
def palace(T=0):
    global _palace
    if _palace is None:
        img = E.grad([(0, (120, 30, 60)), (0.65, (190, 70, 80)), (1, (190, 70, 80))], W, H)
        d = ImageDraw.Draw(img)
        for x in (60, 900):
            d.rectangle([x, 380, x + 120, 1330], fill=(240, 200, 120), outline=OUTL, width=6)
            d.rectangle([x - 20, 360, x + 140, 400], fill=(250, 214, 140), outline=OUTL, width=6)
        d.pieslice([300, 360, 780, 840], 180, 360, fill=(150, 44, 74))
        d.rectangle([0, 1330, W, H], fill=(214, 160, 96))
        for x in range(0, W, 120):
            d.line([(x, 1330), (x - 200, H)], fill=(190, 136, 80), width=4)
        _palace = img
    return _palace

def board(frame, d, x0, y0, s, upto, hi=None, T=0):
    q = s / 8
    d.rectangle([x0 - 10, y0 - 10, x0 + s + 10, y0 + s + 10], fill=(110, 60, 30), outline=OUTL, width=6)
    for i in range(64):
        r, c = divmod(i, 8)
        col = (240, 220, 180) if (r + c) % 2 == 0 else (150, 96, 56)
        x, y = x0 + c * q, y0 + r * q
        d.rectangle([x, y, x + q, y + q], fill=col)
        if i < upto:
            n = min(4, 1 + i // 6)
            for k in range(n):
                grain(d, x + q * (0.3 + 0.4 * ((k * 7) % 3) / 2), y + q * (0.3 + 0.4 * (k % 2)), max(3, q * 0.1), k * 1.1)
        if hi is not None and i == hi:
            p = 0.5 + 0.5 * math.sin(T * 8)
            d.rectangle([x, y, x + q, y + q], outline=(255, 230, int(60 + 120 * p)), width=8)

# ----------------------------------------------------------- props per scene
def legend_props(frame, d, T, sc):
    board(frame, d, 420, 1040, 220, 0)

def legend_after(frame, d, T, sc):
    comp(frame, draw_char("uncle", 340, T, 0, E.blink_at(T, 0.3), (-0.6, 0.1), "crown"), 640, 860)

def first_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = min(10, int(lt / 0.45) + 1)
    board(frame, d, 600, 880, 400, n, n - 1, T)

def spoon_props(frame, d, T, sc):
    cx, cy = 740, 1150
    d.line([(cx + 120, cy - 10), (cx + 200, cy - 140)], fill=OUTL, width=34)
    d.line([(cx + 120, cy - 10), (cx + 200, cy - 140)], fill=(200, 205, 215), width=22)
    d.ellipse([cx - 160, cy - 70, cx + 160, cy + 70], fill=(200, 205, 215), outline=OUTL, width=7)
    mound(d, cx, cy + 10, 240, 70, 1, 18)
    put_label(frame, "1,024 GRAINS", 560, 880)

def sack_props(frame, d, T, sc):
    cx = 760
    d.rounded_rectangle([cx - 170, 930, cx + 170, 1320], radius=60, fill=(214, 180, 120), outline=OUTL, width=7)
    d.polygon([(cx - 90, 950), (cx, 880), (cx + 90, 950)], fill=(214, 180, 120), outline=OUTL)
    d.line([(cx - 80, 940), (cx + 80, 940)], fill=(120, 80, 40), width=12)
    put_label(frame, "20 KG", cx, 1080, 80, (120, 60, 30))

def truck_props(frame, d, T, sc):
    x0, y = 560, 1260
    d.rectangle([x0, y - 200, x0 + 340, y - 40], fill=(60, 140, 90), outline=OUTL, width=7)
    mound(d, x0 + 170, y - 200, 330, 120, 2, 22)
    d.rectangle([x0 + 340, y - 160, x0 + 450, y - 40], fill=(240, 170, 50), outline=OUTL, width=7)
    d.rectangle([x0 + 365, y - 140, x0 + 430, y - 95], fill=(180, 220, 250), outline=OUTL, width=4)
    for wx in (x0 + 70, x0 + 260, x0 + 390):
        d.ellipse([wx - 42, y - 82, wx + 42, y + 2], fill=(40, 40, 46), outline=OUTL, width=5)
        d.ellipse([wx - 14, y - 54, wx + 14, y - 26], fill=(170, 170, 180))
    put_label(frame, "ABOUT 20 TONNES", 560, 870, 56)

def ship_props(frame, d, T, sc):
    bob = 6 * math.sin(T * 2)
    d.rectangle([0, 1250, W, 1360], fill=(40, 110, 190))
    y = 1250 + bob
    d.polygon([(520, y - 140), (1060, y - 140), (1000, y + 20), (580, y + 20)], fill=(200, 60, 60), outline=OUTL)
    mound(d, 790, y - 140, 480, 170, 3, 28)
    d.rectangle([960, y - 260, 1020, y - 140], fill=WHITE, outline=OUTL, width=5)
    for k in range(5):
        x = (k * 230 + T * 60) % W
        d.arc([x - 50, 1262, x + 50, 1300], 200, 340, fill=WHITE, width=5)
    put_label(frame, "ABOUT 22,000 TONNES", 630, 850, 50)

def india_props(frame, d, T, sc):
    mound(d, 540, 1360, 1300, 420, 4, 60)
    d.rectangle([140, 1250, 200, 1290], fill=(60, 140, 90), outline=OUTL, width=3)
    put_label(frame, "2x INDIA'S YEARLY HARVEST", 540, 840, 54)

def total_props(frame, d, T, sc):
    lt = T - sc["s"]
    h = 300 + 300 * ease_out(clamp(lt / 3))
    mound(d, 540, 1380, 1500, h, 5, 70)
    put_label(frame, "18,446,744,073,709,551,615", 540, 380, 54, WHITE)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp(lt / 1.5))
    # two bars: all 63 squares vs last square
    base = 1290
    hA = 400 * p; hB = 400 * p + 4
    d.rectangle([560, base - hA, 700, base], fill=(150, 96, 56), outline=OUTL, width=6)
    d.rectangle([750, base - hB, 890, base], fill=(255, 200, 40), outline=OUTL, width=6)
    if p > 0.3:
        put_label(frame, "1-63", 630, base - hA + 14, 44, WHITE)
        put_label(frame, "64", 820, base - hB + 14, 44, WHITE)
    if lt > 1.6:
        put_label(frame, "+1 GRAIN", 820, base - hB - 76, 44, YEL)

def outro_extra(): return None

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="legend", s=4.0, e=11.0, bg_fn=palace, clock="THE LEGEND", char="kid", pos=(230, 1000, 340),
         props=legend_props, props_after=legend_after, look=(0.6, 0),
         narr="Old Indian legend: the inventor of chess asks the king for RICE.", n_at=4.2,
         say="1 grain, then DOUBLE it each square!", say_at=6.6, pitch=600),
    dict(id="first", s=11.0, e=17.5, bg_fn=palace, clock="SQUARES 1-10", char="uncle", state="crown",
         pos=(300, 1110, 440), props=first_props, look=(0.6, 0.2),
         narr="Square 1: ONE grain. Square 2: TWO. Then 4, 8, 16...", n_at=11.2,
         say="Ha! That's ALL you want?", say_at=13.6, pitch=300),
    dict(id="spoon", s=17.5, e=24.0, bg_fn=palace, clock="SQUARE 11", char="kid", pos=(300, 1110, 420),
         props=spoon_props, look=(0.6, 0.2),
         narr="Square 11: 1,024 grains. About ONE spoonful.", n_at=17.7,
         say="Keep going, MAHARAJ!", say_at=20.0, pitch=600),
    dict(id="sack", s=24.0, e=30.5, bg_fn=palace, clock="SQUARE 21", char="uncle", state="crown",
         pos=(300, 1110, 440), props=sack_props, look=(0.6, 0.1),
         narr="Square 21: over 1 MILLION grains. A 20 kg SACK.", n_at=24.2,
         say="Wait... WHAT?", say_at=26.6, pitch=300),
    dict(id="truck", s=30.5, e=37.0, bg="gully", clock="SQUARE 31", char="uncle", state="crown",
         pos=(250, 1150, 380), props=truck_props, look=(0.6, 0.1),
         narr="Square 31: over 1 BILLION grains. A whole TRUCK.", n_at=30.7,
         say="Call the ACCOUNTANT!", say_at=33.0, pitch=300),
    dict(id="ship", s=37.0, e=43.5, bg="sea1721", clock="SQUARE 41", char="uncle", state="crown_angry",
         pos=(240, 1150, 360), props=ship_props, look=(0.6, 0.1),
         narr="Square 41: over 1 TRILLION grains. A full CARGO SHIP.", n_at=37.2,
         say="This is a SCAM!", say_at=39.6, pitch=280),
    dict(id="india", s=43.5, e=50.5, bg="digsite", clock="SQUARE 55", char="kid", pos=(540, 1020, 300),
         props=india_props, look=(0, 0.3),
         narr="Square 55 ALONE: more than DOUBLE the rice India grows in a year.", n_at=43.7,
         say="India grows the MOST, too!", say_at=46.4, pitch=620),
    dict(id="total", s=50.5, e=57.5, bg="digsite", clock="ALL 64 SQUARES", char="uncle", state="crown_angry",
         pos=(540, 1000, 300), props=total_props, look=(0, 0.2),
         narr="Total: 18 QUINTILLION grains. Over 500 YEARS of the whole world's rice.", n_at=50.7,
         say="I'm BANKRUPT!", say_at=53.6, pitch=280),
    dict(id="twist", s=57.5, e=65.0, bg="twist", clock="THE TWIST", char="kid", pos=(300, 1110, 420),
         props=twist_props, twist=True, look=(0.6, 0.2),
         narr="And the LAST square alone holds MORE than all 63 before it, COMBINED.", n_at=57.7,
         say="That's how DOUBLING works!", say_at=60.6, pitch=600),
    dict(id="outro", s=65.0, e=70.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        for k in range(7):
            grain(d, 540 + (k - 3) * 70, 1420 + 30 * math.sin(T * 4 + k), 16 * p, k * 0.7)

cfg = dict(
    total=70.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("1 GRAIN OF RICE", WHITE)], 120), 770, 0.75, "right"),
        (title([("DOUBLED", YEL)], 150), 915, 1.05, "left"),
        (title([("on every ", WHITE), ("CHESS SQUARE?", YEL)], 88), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would", WHITE), (" YOU", YEL)], 92), 470, 0.15),
                      (title([("have taken the deal?", WHITE)], 84), 600, 0.45)],
               row=[("kid", 1), ("uncle", "crown"), ("ladoo", 1), ("chai", 1), ("earth", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=57.35), dict(t0=65.0, t1=70.0, melody=True)],
    drones=[dict(t0=57.5, dur=7.5, g=0.08)],
    fx=[("pop", 11.4, 0.6), ("pop", 11.9, 0.6), ("pop", 12.3, 0.6), ("pop", 12.8, 0.6),
        ("crash", 24.3, 0.4), ("rumble", 30.8, 0.4, dict(dd=3.0)), ("waves", 37.1, 0.5, dict(dd=6.0)),
        ("rumble", 43.8, 0.6, dict(dd=4.0)), ("boom", 50.8, 1.0)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_rice_chessboard")
