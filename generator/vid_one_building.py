#!/usr/bin/env python3
"""What if all 8.3 billion humans lived in ONE building?"""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def tower(d, x0, x1, ytop, ybot, T, lit=True, col=(120, 140, 170)):
    d.rectangle([x0, ytop, x1, ybot], fill=col, outline=OUTL, width=6)
    cols = max(2, int((x1 - x0) / 34))
    for r in range(int((ybot - ytop) / 40)):
        for c in range(cols):
            wx = x0 + 10 + c * (x1 - x0 - 20) / cols
            wy = ytop + 12 + r * 40
            on = lit and ((r * 7 + c * 3 + int(T * 2)) % 5 != 0)
            d.rectangle([wx, wy, wx + 18, wy + 22], fill=(255, 226, 120) if on else (70, 84, 110))

def rooms_props(frame, d, T, sc):
    for side in (0, 1):
        for r in range(5):
            for c in range(2):
                x = (40 if side == 0 else 800) + c * 120; y = 820 + r * 105
                d.rectangle([x, y, x + 100, y + 90], fill=(250, 244, 230), outline=OUTL, width=5)
                comp(frame, draw_char("kid" if (r + c + side) % 2 else "uncle", 70, T, 0, False, (0, 0), 1), x + 15, y + 12)

def plot_props(frame, d, T, sc):
    # top-down plot, 1 km x 1 km, filling up with rooms
    x0, y0, s = 270, 860, 540
    d.rectangle([x0, y0, x0 + s, y0 + s], fill=(170, 200, 130), outline=OUTL, width=8)
    q = clamp((T - sc["s"] - 0.6) / 4.5)
    n = 20
    for i in range(int(q * n * n)):
        r, c = divmod(i, n)
        x = x0 + 6 + c * (s - 12) / n; y = y0 + 6 + r * (s - 12) / n
        d.rectangle([x + 2, y + 2, x + (s - 12) / n - 2, y + (s - 12) / n - 2], fill=(250, 240, 220))
    l = label("1 KM", 54, YEL)
    comp(frame, l, x0 - l.width - 14, y0 + s / 2 - l.height / 2)

def floors_props(frame, d, T, sc):
    # endless tower on the left, tiny Burj Khalifa beside it
    tower(d, 60, 300, -40, 1700, T)
    bx = 360
    d.polygon([(bx, 1700), (bx + 70, 1700), (bx + 40, 1560), (bx + 35, 1520), (bx + 30, 1560)], fill=(200, 210, 225),
              outline=OUTL)

def snow_peak(frame, d, T, sc):
    tower(d, 40, 230, -40, 1920, T)
    d.polygon([(560, 1920), (1080, 1920), (1080, 1500), (900, 1250), (760, 1400)], fill=(150, 150, 170), outline=OUTL)
    d.polygon([(840, 1330), (900, 1250), (960, 1335), (920, 1310), (880, 1345)], fill=WHITE)
    for k in range(20):
        x = (k * 97 + 40 * math.sin(T + k)) % W
        y = (k * 173 + T * (60 + k % 5 * 15)) % H
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=WHITE)

def plane_props(frame, d, T, sc):
    tower(d, 40, 230, -40, 1920, T)
    lt = T - sc["s"]
    x = 1150 - (lt * 170) % 1500; y = 980
    d.polygon([(x, y), (x + 260, y - 10), (x + 300, y - 70), (x + 320, y - 70), (x + 300, y + 10), (x + 40, y + 30)],
              fill=WHITE, outline=OUTL)
    d.polygon([(x + 120, y + 5), (x + 200, y + 5), (x + 150, y + 80)], fill=(200, 210, 225), outline=OUTL)
    for k in range(5):
        d.ellipse([x + 60 + k * 36, y - 2, x + 76 + k * 36, y + 14], fill=(80, 120, 190))

def space_tower(frame, d, T, sc):
    tower(d, 40, 230, -40, 1920, T)
    for k in range(40):
        x = (k * 263) % W; y = (k * 401) % 1800
        if x < 260: continue
        r = 2 + (k % 3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

def top_props(frame, d, T, sc):
    tower(d, 40, 230, 1200, 1920, T)
    d.polygon([(40, 1200), (230, 1200), (135, 1120)], fill=(225, 50, 60), outline=OUTL)
    # the space station, still higher up
    x = 700 + 160 * math.sin(T * 0.6); y = 470
    d.rectangle([x - 30, y - 16, x + 30, y + 16], fill=(220, 220, 230), outline=OUTL, width=4)
    for sx in (-1, 1):
        d.rectangle([x + sx * 85 - 45, y - 30, x + sx * 85 + 45, y + 30], fill=(60, 90, 170), outline=OUTL, width=4)

def lift_props(frame, d, T, sc):
    tower(d, 60, 260, -40, 1920, T, col=(150, 160, 180))
    lt = T - sc["s"]
    y = 1700 - (lt * 60) % 1600
    d.rectangle([125, y - 60, 195, y], fill=(255, 214, 10), outline=OUTL, width=5)
    for k in range(3):
        d.line([(110, y + 20 + k * 30), (210, y + 20 + k * 30)], fill=(255, 255, 255), width=3)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="rooms", s=4.0, e=11.0, bg="office", clock="8.3 BILLION PEOPLE", char="kid", pos=(540, 1060, 500),
         props=rooms_props, look=(0, 0.1),
         narr="Give every one of 8.3 BILLION people a tiny 10 square metre room.", n_at=4.2,
         say="My room? It's a BOX!", say_at=6.6, pitch=600),
    dict(id="plot", s=11.0, e=18.0, bg="day", clock="1 KM x 1 KM PLOT", char="uncle", pos=(540, 1130, 340),
         props=plot_props, look=(0, 0.2),
         narr="Stack them on a 1 km by 1 km plot: 1 LAKH rooms per floor.", n_at=11.2,
         say="1 lakh neighbours? NO privacy!", say_at=13.8, pitch=230),
    dict(id="floors", s=18.0, e=25.0, bg="day", clock="83,000 FLOORS", char="kid", pos=(700, 1080, 480),
         props=floors_props, look=(-0.5, -0.4),
         narr="That's about 83,000 FLOORS. Burj Khalifa has just 163.", n_at=18.2,
         say="Lift ka button KAHAN hai?", say_at=20.8, pitch=600),
    dict(id="everest", s=25.0, e=32.0, bg="pole", clock="FLOOR 2,950", char="uncle", pos=(560, 1080, 440),
         props=snow_peak, look=(0.5, 0),
         narr="Floor 2,950: you're level with the top of EVEREST.", n_at=25.2,
         say="Free view. Free SNOW.", say_at=27.6, pitch=230),
    dict(id="planes", s=32.0, e=39.0, bg="day", clock="FLOOR 3,700", char="kid", pos=(620, 1300, 440),
         props=plane_props, look=(0.4, -0.3),
         narr="Floor 3,700: planes cruise right PAST your window.", n_at=32.2,
         say="Window seat, but FREE!", say_at=34.6, pitch=600),
    dict(id="space", s=39.0, e=46.0, bg="space", clock="FLOOR 33,000+", char="kid", pos=(620, 1080, 460),
         props=space_tower, look=(0, -0.3),
         narr="Around floor 33,000 you pass 100 KM up. Officially SPACE.", n_at=39.2,
         say="Mummy, I'm an ASTRONAUT!", say_at=41.8, pitch=620),
    dict(id="top", s=46.0, e=53.0, bg="space", clock="TOP FLOOR: ~250 KM", char="earth", pos=(640, 1100, 440),
         props=top_props, look=(-0.3, 0.2),
         narr="The roof is about 250 KM up. The space station still orbits higher, at 400 KM.", n_at=46.2,
         say="Tall tower. Still SHORT.", say_at=49.4, pitch=200),
    dict(id="twist", s=53.0, e=61.0, bg="office", clock="THE CATCH", char="uncle", state="angry",
         pos=(640, 1080, 520), props=lift_props, twist=True, look=(-0.3, 0),
         narr="Fastest lift on Earth: 21 metres a second. Ground to roof: over 3 HOURS.", n_at=53.2,
         say="I FORGOT my phone downstairs!", say_at=56.6, pitch=220),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        h = 420 * p
        dd = ImageDraw.Draw(frame)
        tower(dd, 470, 610, 1700 - h, 1700, T)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("ALL 8 BILLION", WHITE)], 124), 770, 0.75, "right"),
        (title([("HUMANS LIVED IN", WHITE)], 110), 905, 1.05, "left"),
        (title([("ONE ", WHITE), ("BUILDING?", YEL)], 110), 1050, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which floor would ", WHITE), ("YOU", YEL)], 84), 470, 0.15),
                      (title([("live on?", YEL)], 120), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("earth", 1), ("uncle", "angry"), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=39.0), dict(t0=39.0, t1=52.85, melody=True),
           dict(t0=61.0, t1=66.0, melody=True)],
    drones=[dict(t0=39.0, dur=14.0, g=0.06)],
    fx=[("crowd", 4.3, 0.4, dict(dd=5.0)), ("wind", 25.0, 0.6, dict(dd=7.0)), ("rumble", 32.3, 0.5, dict(dd=4.0)),
        ("ding", 59.5, 0.5)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_all_humans_lived_in_one_building")
