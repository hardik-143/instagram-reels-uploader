#!/usr/bin/env python3
"""What if you grew 1 cm every second?
Maths: 1 cm/s = 60 cm a minute, 36 m an hour, 864 m a day, ~315 km a year.
Facts (checked 2026-11-17):
- Qutub Minar 72.5 m (UNESCO / ASI; same figure used in vid_paper_fold.py) -> ~2 hours.
- Burj Khalifa 828 m (CTBUH Skyscraper Center) -> passed inside 1 day (864 m).
- Everest 8,849 m -> ~10 days 6 hours; summit air ~30-34 kPa, about a third of sea level (hypertextbook.com).
- ISS orbits ~400 km up (NASA) -> ~1.3 years; 1 year = ~315 km.
- Moon ~384,400 km -> 3.8e10 s, ~1,200 years.
- Square-cube law, Galileo, Two New Sciences (1638): 2x size -> 4x bone strength (area) but 8x weight
  (volume) (Scientific American, 2026, '388 years ago Galileo worked out why human giants can't exist').
- Tallest human ever measured: 2.72 m (Guinness World Records).
- Blue whales >30 m: water's buoyancy carries the weight that limits land animals (Popular Science).
"""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 53.0
GROUND = 1330
SHIRT = (250, 140, 60)
JEANS = (60, 90, 170)
SKIN = (242, 194, 152)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=56, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

_head = {}
def head(B, T):
    return draw_char("kid", int(B), T, 0, E.blink_at(T, 0.3), (0, -0.2), 1)

def giant(frame, d, T, cx, ground, h):
    """Cartoon kid standing on `ground`, total height h px (head ~22%)."""
    h = max(h, 160)
    hb = max(70, h * 0.24)
    body = h - hb * 0.85
    w = max(26, body * 0.30)
    leg = body * 0.48
    torso = body - leg
    top = ground - body
    # legs
    d.rounded_rectangle([cx - w / 2, ground - leg, cx - 3, ground], 8, fill=JEANS, outline=OUTL, width=4)
    d.rounded_rectangle([cx + 3, ground - leg, cx + w / 2, ground], 8, fill=JEANS, outline=OUTL, width=4)
    # arms
    aw = max(10, w * 0.22)
    d.rounded_rectangle([cx - w / 2 - aw, top + 6, cx - w / 2 + 2, top + torso * 0.95], 8, fill=SKIN, outline=OUTL, width=4)
    d.rounded_rectangle([cx + w / 2 - 2, top + 6, cx + w / 2 + aw, top + torso * 0.95], 8, fill=SKIN, outline=OUTL, width=4)
    # torso
    d.rounded_rectangle([cx - w / 2, top, cx + w / 2, top + torso + 10], 12, fill=SHIRT, outline=OUTL, width=5)
    comp(frame, head(hb, T), cx - hb / 2, top - hb * 0.85)

def grow(sc, T, a=0.0, b=1.0, dur=1.6):
    return a + (b - a) * ease_out(clamp((T - sc["s"] - 0.3) / dur))

def ground(d, col=(110, 170, 90)):
    d.rectangle([0, GROUND, W, H], fill=col)
    d.line([(0, GROUND), (W, GROUND)], fill=OUTL, width=6)

# ---------------------------------------------------------------- landmarks
def door(d, x, base, h):
    w = h * 0.45
    d.rectangle([x - w / 2, base - h, x + w / 2, base], fill=(150, 100, 60), outline=OUTL, width=6)
    d.ellipse([x + w / 2 - 30, base - h / 2 - 10, x + w / 2 - 12, base - h / 2 + 8], fill=YEL, outline=OUTL, width=3)

def building(d, x, base, floors, fh, w=200):
    for k in range(floors):
        y = base - (k + 1) * fh
        d.rectangle([x - w / 2, y, x + w / 2, y + fh], fill=(250, 190, 150), outline=OUTL, width=3)
        for j in (-1, 1):
            d.rectangle([x + j * w / 4 - 16, y + fh * 0.25, x + j * w / 4 + 16, y + fh * 0.75], fill=(180, 220, 250))

def qutub(d, cx, base, h):
    w0, w1 = h * 0.2, h * 0.07
    d.polygon([(cx - w0 / 2, base), (cx - w1 / 2, base - h), (cx + w1 / 2, base - h), (cx + w0 / 2, base)],
              fill=(200, 110, 80), outline=OUTL)
    for k in range(1, 5):
        y = base - h * k / 5
        ww = w0 + (w1 - w0) * k / 5
        d.rectangle([cx - ww / 2 - 8, y - 6, cx + ww / 2 + 8, y + 6], fill=(170, 90, 70), outline=OUTL, width=3)

def burj(d, cx, base, h):
    tiers = [(0.0, 0.30, 0.16), (0.30, 0.55, 0.11), (0.55, 0.75, 0.07), (0.75, 0.88, 0.04)]
    for a, b, w in tiers:
        d.rectangle([cx - w * h / 2, base - b * h, cx + w * h / 2, base - a * h], fill=(170, 200, 225), outline=OUTL, width=4)
    d.polygon([(cx - 6, base - 0.88 * h), (cx, base - h), (cx + 6, base - 0.88 * h)], fill=(170, 200, 225), outline=OUTL)

def mountain(d, cx, base, h, w):
    d.polygon([(cx - w / 2, base), (cx, base - h), (cx + w / 2, base)], fill=(120, 120, 140), outline=OUTL)
    s = h * 0.2
    d.polygon([(cx - s * 0.7, base - h + s), (cx, base - h), (cx + s * 0.7, base - h + s),
               (cx + s * 0.25, base - h + s * 0.75), (cx, base - h + s), (cx - s * 0.25, base - h + s * 0.75)],
              fill=WHITE, outline=OUTL)

def iss(d, x, y, s=1.0):
    d.rectangle([x - 70 * s, y - 6 * s, x + 70 * s, y + 6 * s], fill=(200, 200, 210), outline=OUTL, width=3)
    for dx in (-60, -35, 35, 60):
        d.rectangle([x + dx * s - 10 * s, y - 45 * s, x + dx * s + 10 * s, y + 45 * s], fill=(60, 90, 180), outline=OUTL, width=3)
    d.rectangle([x - 16 * s, y - 14 * s, x + 16 * s, y + 14 * s], fill=WHITE, outline=OUTL, width=3)

# ---------------------------------------------------------------- scenes
def door_props(frame, d, T, sc):
    ground(d, (200, 160, 120))
    door(d, 760, GROUND, 440)
    put_label(frame, "+1 CM EVERY SECOND", 540, 335, 60)
    giant(frame, d, T, 430, GROUND, grow(sc, T, 300, 480))

def house_props(frame, d, T, sc):
    ground(d)
    building(d, 770, GROUND, 10, 55)
    put_label(frame, "10 FLOORS: ~30 M", 540, 335, 60)
    giant(frame, d, T, 380, GROUND, grow(sc, T, 120, 650))

def qutub_props(frame, d, T, sc):
    ground(d)
    qutub(d, 790, GROUND, 630)
    put_label(frame, "QUTUB MINAR: 72.5 M", 540, 335, 60)
    giant(frame, d, T, 400, GROUND, grow(sc, T, 320, 625))

def burj_props(frame, d, T, sc):
    ground(d, (230, 200, 140))
    burj(d, 780, GROUND, 610)
    put_label(frame, "BURJ KHALIFA: 828 M", 540, 335, 60)
    giant(frame, d, T, 400, GROUND, grow(sc, T, 60, 640))

def everest_props(frame, d, T, sc):
    ground(d, (180, 190, 200))
    mountain(d, 760, GROUND, 640, 620)
    put_label(frame, "EVEREST: 8,849 M", 540, 335, 60)
    giant(frame, d, T, 330, GROUND, grow(sc, T, 70, 625))

def iss_props(frame, d, T, sc):
    lt = T - sc["s"]
    comp(frame, draw_char("earth", 700, T, 0, False, (0, -0.4), lt * 0.05), 190, 1100)
    put_label(frame, "SPACE STATION: ~400 KM", 540, 335, 60)
    iss(d, 860, 770 + 6 * math.sin(T * 2), 0.9)
    h = grow(sc, T, 60, 540)
    # a long thin you, standing on top of the Earth
    giant(frame, d, T, 540, 1196, h)

def moon_props(frame, d, T, sc):
    lt = T - sc["s"]
    comp(frame, draw_char("earth", 240, T, 0, False, (0.3, -0.3), lt * 0.3), 140, 1000)
    comp(frame, draw_char("moon", 170, T, 0, E.blink_at(T, 0.7), (-0.3, 0.4)), 790, 680)
    p = grow(sc, T, 0, 1, 2.6)
    x0, y0, x1, y1 = 340, 1050, 820, 790
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    d.line([(x0, y0), (xe, ye)], fill=OUTL, width=26)
    d.line([(x0, y0), (xe, ye)], fill=SHIRT, width=16)
    comp(frame, head(110, T), xe - 55, ye - 70)
    put_label(frame, "384,400 KM", 540, 335, 60)

def twist_props(frame, d, T, sc):
    ground(d, (90, 80, 110))
    lt = T - sc["s"]
    # two cubes: 1x and 2x size, showing weight 8x vs bone 4x
    s1, s2 = 120, 240
    d.rectangle([180, GROUND - s1, 180 + s1, GROUND], fill=(250, 190, 150), outline=OUTL, width=5)
    d.rectangle([520, GROUND - s2, 520 + s2, GROUND], fill=(250, 190, 150), outline=OUTL, width=5)
    for k in (1,):
        d.line([(520 + s2 / 2, GROUND - s2), (520 + s2 / 2, GROUND)], fill=OUTL, width=3)
        d.line([(520, GROUND - s2 / 2), (520 + s2, GROUND - s2 / 2)], fill=OUTL, width=3)
    put_label(frame, "1X", 240, GROUND - s1 - 70, 48, WHITE)
    put_label(frame, "2X TALLER", 640, GROUND - s2 - 70, 48, WHITE)
    if lt > 2.5:
        put_label(frame, "WEIGHT X8", 540, 360, 64, (255, 120, 120))
    if lt > 4.0:
        put_label(frame, "BONES X4", 540, 440, 60, YEL)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="minute", s=4.0, e=11.0, bg="day", clock="1 MINUTE", props=door_props,
         narr="You grow 1 CM every second. One minute later: 60 CM taller.", n_at=4.2,
         say="Every door is a LIMBO now!", say_at=6.8, pitch=620, bubble_y=650),
    dict(id="hour", s=11.0, e=18.0, bg="day", clock="1 HOUR", props=house_props,
         narr="One hour: 36 METRES. Taller than a 10-storey building.", n_at=11.2,
         say="Hello, TOP floor!", say_at=13.8, pitch=600, bubble_y=650),
    dict(id="qutub", s=18.0, e=25.0, bg="day", clock="2 HOURS", props=qutub_props,
         narr="Two hours: 72 METRES. Eye to eye with Qutub MINAR.", n_at=18.2,
         say="Namaste, MINAR!", say_at=20.8, pitch=580, bubble_y=650),
    dict(id="day", s=25.0, e=32.0, bg="digsite", clock="1 DAY", props=burj_props,
         narr="One day: 864 METRES. You just passed Burj Khalifa's 828.", n_at=25.2,
         say="I can see DUBAI's roof!", say_at=27.8, pitch=560, bubble_y=650),
    dict(id="everest", s=32.0, e=39.0, bg="pole", clock="10 DAYS", props=everest_props,
         narr="Ten days: 8.6 KM. Your head is near Everest, in THIN air.", n_at=32.2,
         say="A THIRD of the air pressure!", say_at=34.8, pitch=540, bubble_y=650),
    dict(id="year", s=39.0, e=46.0, bg="space", clock="1 YEAR", props=iss_props,
         narr="One year: 315 KM tall. Almost level with the SPACE station.", n_at=39.2,
         say="Wave to the ASTRONAUTS!", say_at=41.8, pitch=520, bubble_y=650),
    dict(id="moon", s=46.0, e=TW, bg="space", clock="1,200 YEARS", props=moon_props,
         narr="To touch the MOON, keep growing for about 1,200 YEARS.", n_at=46.2,
         say="Worth the WAIT?", say_at=48.8, pitch=500, bubble_y=650),
    dict(id="twist", s=TW, e=61.0, bg="night", clock="PLOT TWIST", props=twist_props,
         char="kid", pos=(900, 960, 180), twist=True, enter=TW + 5.0,
         narr="Plot twist: 2x taller = 8x HEAVIER, but bones only 4x STRONGER.", n_at=TW + 0.4,
         say="Galileo knew in 1638!", say_at=TW + 5.4, pitch=640),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        h = 260 + 160 * clamp((T - 2.3) / 1.5)
        dd = ImageDraw.Draw(frame)
        if p > 0.95:
            giant(frame, dd, T, 540, 1700, h)
        else:
            paste_c(frame, head(200, T), 540, 1500, p)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 470, 0.2, "pop"),
        (title([("YOU GREW", WHITE)], 140), 670, 0.75, "right"),
        (title([("1 CM", YEL)], 170), 830, 1.05, "left"),
        (title([("EVERY SECOND?", WHITE)], 120), 990, 1.4, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("How tall would", WHITE)], 92), 470, 0.15),
                      (title([("YOU ", YEL), ("stop?", WHITE)], 110), 600, 0.45)],
               row=[("kid", 1), ("earth", 0), ("moon", 1), ("whale", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=61.0, t1=66.0, melody=True)],
    fx=[("wind", 32.2, 0.35, dict(dd=6.0)), ("rumble", 25.3, 0.3, dict(dd=2.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_grew_1cm_every_second")
