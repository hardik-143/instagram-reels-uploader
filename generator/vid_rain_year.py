#!/usr/bin/env python3
"""What if it rained nonstop for a year? Facts: 'petrichor' coined by Australian scientists Isabel Joy Bear and
R. G. Thomas in Nature, 1964; much of the smell is geosmin, made by soil bacteria (actinomycetes); some people can
detect geosmin at ~5 parts per trillion (Smithsonian, 'What Makes Rain Smell So Good?'); small raindrops (radius < 1 mm)
are spherical, larger ones are shaped like a hamburger bun, and above ~4.5 mm radius (~9 mm across) they distort into
a parachute shape and break apart (USGS Water Science School, 'Are Raindrops Shaped Like Teardrops?');
if all the water in the atmosphere fell at once it would cover Earth only ~2.5 cm deep; ~450 cubic km of water
evaporate or transpire into the air each day (NOAA JetStream 'Water, Water Everywhere').
Our arithmetic (hypothetical drizzle of 2.5 mm/h): 60 mm/day, ~22 m/year if none drained; the sky's 25 mm lasts
~10 hours; 60 mm/day over Earth's ~510 million km2 = ~30,600 km3/day, ~70x the 450 km3/day evaporated."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
BLUE = (90, 160, 235)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=56, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def rain(d, T, n=60, speed=1500, col=(200, 220, 255), slant=0.25, ymax=1330):
    for i in range(n):
        x0 = (i * 157) % (W + 200) - 100
        y = (T * speed + i * 263) % (ymax + 200) - 200
        x = x0 + slant * y * 0.3
        d.line([(x, y), (x - 60 * slant, y + 60)], fill=col, width=5)

def ground(d, col=(120, 90, 60)):
    d.rectangle([0, 1330, W, 1400], fill=col)
    d.line([(0, 1330), (W, 1330)], fill=OUTL, width=6)

# ------------------------------------------------------------- scene props
def smell_props(frame, d, T, sc):
    rain(d, T, 40)
    ground(d)
    # soil puffs rising
    lt = T - sc["s"]
    for k in range(6):
        ph = (lt * 0.5 + k / 6) % 1.0
        x = 640 + k * 70 + 20 * math.sin(T * 2 + k)
        y = 1320 - ph * 380
        r = 18 + 30 * ph
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], outline=(200, 170, 120), width=5)

def geo_props(frame, d, T, sc):
    rain(d, T, 30)
    ground(d)
    lt = T - sc["s"]
    # soil bacteria as little wiggles in the dirt
    for k in range(7):
        x = 600 + k * 60; y = 1355 + 10 * math.sin(T * 3 + k)
        d.arc([x - 25, y - 12, x + 25, y + 12], 0, 360, fill=(90, 200, 120), width=6)
    if lt > 0.5: put_label(frame, "5 PARTS PER TRILLION", 540, 380, 70)

def drop_shape(d, cx, cy, kind, s=1.0):
    if kind == "tear":
        d.polygon([(cx, cy - 110 * s), (cx - 62 * s, cy + 10 * s), (cx + 62 * s, cy + 10 * s)], fill=BLUE)
        d.ellipse([cx - 70 * s, cy - 50 * s, cx + 70 * s, cy + 90 * s], fill=BLUE, outline=OUTL, width=6)
    elif kind == "round":
        d.ellipse([cx - 60 * s, cy - 60 * s, cx + 60 * s, cy + 60 * s], fill=BLUE, outline=OUTL, width=6)
    elif kind == "bun":
        d.chord([cx - 95 * s, cy - 80 * s, cx + 95 * s, cy + 80 * s], 180, 360, fill=BLUE, outline=OUTL, width=6)
        d.rectangle([cx - 95 * s, cy - 4 * s, cx + 95 * s, cy + 18 * s], fill=BLUE)
        d.line([(cx - 95 * s, cy + 18 * s), (cx + 95 * s, cy + 18 * s)], fill=OUTL, width=6)
        d.line([(cx - 95 * s, cy - 2 * s), (cx - 95 * s, cy + 18 * s)], fill=OUTL, width=6)
        d.line([(cx + 95 * s, cy - 2 * s), (cx + 95 * s, cy + 18 * s)], fill=OUTL, width=6)
    elif kind == "chute":
        d.chord([cx - 130 * s, cy - 90 * s, cx + 130 * s, cy + 90 * s], 180, 360, outline=OUTL, width=6, fill=(150, 200, 250))
        d.ellipse([cx - 130 * s, cy - 14 * s, cx + 130 * s, cy + 24 * s], fill=BLUE, outline=OUTL, width=6)

def shape_props(frame, d, T, sc):
    lt = T - sc["s"]
    p1 = ease_out(clamp((lt - 0.3) / 0.6)); p2 = ease_out(clamp((lt - 2.0) / 0.6)); p3 = ease_out(clamp((lt - 3.2) / 0.6))
    if p1 > 0:
        drop_shape(d, 200, 1000, "tear", p1 * 1.2)
        if lt < 2.6: put_label(frame, "MYTH", 200, 1110, 50, (255, 120, 110))
        else:
            d.line([(110, 900), (290, 1100)], fill=(230, 50, 40), width=14)
            d.line([(290, 900), (110, 1100)], fill=(230, 50, 40), width=14)
    if p2 > 0:
        drop_shape(d, 540, 1020, "round", p2 * 0.7)
        put_label(frame, "SMALL", 540, 1110, 46, WHITE)
    if p3 > 0:
        drop_shape(d, 860, 1030, "bun", p3 * 1.25)
        put_label(frame, "BIGGER", 860, 1110, 46, YEL)

def chute_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = clamp((lt - 0.4) / 3.0)
    y = 900 + 60 * math.sin(T * 2)
    if g < 0.75:
        drop_shape(d, 760, y, "bun", 1.0 + 0.4 * g)
    else:
        drop_shape(d, 760, y, "chute", 1.0)
    if lt > 4.6:
        for k, (dx, dy) in enumerate(((-150, 230), (-50, 280), (60, 250), (160, 220))):
            drop_shape(d, 760 + dx, y + dy + (lt - 4.6) * 60, "round", 0.35)
    if lt > 0.5: put_label(frame, "OVER 9 mm: SPLAT", 540, 380, 74)

def day_props(frame, d, T, sc):
    rain(d, T, 35, 1200)
    lt = T - sc["s"]
    # rain gauge
    x0, x1, top, base = 800, 960, 900, 1300
    d.rectangle([x0, top, x1, base], fill=(235, 245, 255), outline=OUTL, width=7)
    lvl = base - (base - top) * 0.6 * ease_out(clamp((lt - 0.5) / 4.0))
    if lvl < base - 7: d.rectangle([x0 + 7, lvl, x1 - 7, base - 7], fill=BLUE)
    for k in range(1, 6):
        y = base - k * (base - top) / 6
        d.line([(x1 - 40, y), (x1 - 7, y)], fill=OUTL, width=4)
    put_label(frame, f"{round(60 * ease_out(clamp((lt - 0.5) / 4.0)))} mm", 880, 815, 56)
    ground(d)

def year_props(frame, d, T, sc):
    rain(d, T, 50, 1700)
    lt = T - sc["s"]
    x0, x1, base, fh = 600, 880, 1320, 60
    for f in range(7):
        y = base - (f + 1) * fh
        d.rectangle([x0, y, x1, y + fh], fill=(240, 220, 190), outline=OUTL, width=4)
        for c in range(3):
            wx = x0 + 28 + c * 85
            d.rectangle([wx, y + 16, wx + 50, y + fh - 16], fill=(160, 210, 250), outline=OUTL, width=3)
    lvl = 7 * fh * ease_out(clamp((lt - 0.4) / 3.6))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(img)
    dd.rectangle([0, base - lvl + 8 * math.sin(T * 4), W, 1400], fill=(60, 130, 210, 150))
    frame.alpha_composite(img)
    put_label(frame, "ABOUT 22 M", 740, base - 7 * fh - 78, 60)

def tank_props(frame, d, T, sc):
    lt = T - sc["s"]
    # thin water layer over a globe slice
    d.ellipse([-300, 1150, 1380, 2100], fill=(70, 150, 90), outline=OUTL, width=8)
    th = 26 * ease_out(clamp((lt - 0.5) / 1.5))
    d.arc([-300 - th, 1150 - th, 1380 + th, 2100 + th], 200, 340, fill=BLUE, width=max(1, int(th)))
    if lt > 0.5: put_label(frame, "ONLY ABOUT 2.5 CM", 540, 380, 80)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # clock face counting 10 hours, cloud shrinking (cloud is the char)
    cx, cy, r = 820, 930, 140
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=OUTL, width=10)
    hrs = min(10.0, 10.0 * clamp((lt - 0.5) / 3.5))
    a = math.radians(90 - hrs * 30)
    d.line([(cx, cy), (cx + math.cos(a) * r * 0.75, cy - math.sin(a) * r * 0.75)], fill=(230, 50, 40), width=10)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=OUTL)
    put_label(frame, f"{int(hrs)} HOURS", cx, cy + r + 30, 56)
    if lt > 0.5: put_label(frame, "SKY: EMPTY", 540, 380, 90)

def cloud_pos(T):
    lt = T - TW
    s = 440 - 200 * clamp((lt - 0.5) / 3.5)
    return (300, 1060, int(s))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="smell", s=4.0, e=11.0, bg="storm", clock="HOUR 1", char="kid", pos=(320, 1100, 420),
         props=smell_props, look=(0.6, 0.3),
         narr="That earthy smell has a name: PETRICHOR. Scientists named it in 1964.", n_at=4.2,
         say="Smells like wet MITTI!", say_at=7.2, pitch=600),
    dict(id="geo", s=11.0, e=18.0, bg="storm", clock="HOUR 1", char="kid", pos=(320, 1100, 420),
         props=geo_props, look=(0.6, 0.4),
         narr="Soil bacteria make GEOSMIN. Some noses catch it at 5 PARTS per TRILLION.", n_at=11.2,
         say="My nose is a SUPERHERO!", say_at=14.4, pitch=620),
    dict(id="shape", s=18.0, e=25.0, bg="storm", clock="HOUR 2", char="kid", pos=(540, 1295, 130),
         props=shape_props, look=(0, -0.5),
         narr="Raindrops aren't TEARDROPS. Small ones are round, bigger ones look like BURGER BUNS.",
         n_at=18.2, say="Bun? Where's the PATTY?", say_at=21.6, pitch=620),
    dict(id="chute", s=25.0, e=32.0, bg="storm", clock="HOUR 3", char="kid", pos=(280, 1100, 380),
         props=chute_props, look=(0.6, -0.4),
         narr="Drops over about 9 mm wide puff into a PARACHUTE and BREAK apart.", n_at=25.2,
         say="Raindrop with a PARACHUTE?!", say_at=28.2, pitch=620),
    dict(id="day", s=32.0, e=39.0, bg="storm", clock="DAY 1", char="chai", pos=(330, 1100, 380),
         props=day_props, look=(0.6, 0),
         narr="Say it drizzles 2.5 mm an hour, NONSTOP. That's 60 mm EVERY day.", n_at=32.2,
         say="Pakoda weather FOREVER!", say_at=35.2, pitch=420),
    dict(id="year", s=39.0, e=46.0, bg="storm", clock="DAY 365", char="kid", state="puff",
         pos=(280, 1100, 380), props=year_props, look=(0.6, -0.3),
         narr="After a YEAR: about 22 METRES of rain, if none drained away.", n_at=39.2,
         say="That's a 7-STOREY building!", say_at=42.2, pitch=640),
    dict(id="tank", s=46.0, e=TW, bg="space", clock="BUT WAIT", char="cloud", pos=(540, 940, 420),
         props=tank_props, look=(0, 0.3),
         narr="But ALL the water in the sky would cover Earth only about 2.5 CM deep.",
         n_at=46.2, say="I'm a TINY tank!", say_at=49.4, pitch=420),
    dict(id="twist", s=TW, e=61.0, bg="storm", clock="PLOT TWIST", char="cloud", pos=cloud_pos,
         props=twist_props, twist=True, look=(0.6, 0),
         narr="Twist: at that rate, the WHOLE sky runs DRY in about 10 HOURS!",
         n_at=TW + 0.2, say="I'm all RAINED OUT!", say_at=TW + 3.8, pitch=420),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        rain(d, T, 40, 1600, (200, 220, 255), 0.25, 1920)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("IT RAINED", WHITE)], 130), 770, 0.75, "right"),
        (title([("NONSTOP", YEL)], 150), 915, 1.05, "left"),
        (title([("for a YEAR?", WHITE)], 110), 1075, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Could", WHITE), (" YOU", YEL), (" handle", WHITE)], 92), 470, 0.15),
                      (title([("a year of rain?", WHITE)], 92), 600, 0.45)],
               row=[("kid", 1), ("cloud", 1), ("chai", 1), ("flower", 1), ("fish", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0, melody=True), dict(t0=32.0, t1=46.0),
           dict(t0=46.0, t1=TW - 0.15, minor=True), dict(t0=61.0, t1=66.0, melody=True)],
    drones=[dict(t0=TW, dur=8.0, g=0.08)],
    fx=[("wind", 4.1, 0.25, dict(dd=14.0)), ("splash", 28.6, 0.4), ("gale", 32.1, 0.25, dict(dd=14.0)),
        ("waves", 39.6, 0.35, dict(dd=6.0)), ("powerdown", TW + 3.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_it_rained_nonstop_for_a_year")
