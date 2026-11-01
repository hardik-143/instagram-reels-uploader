#!/usr/bin/env python3
"""What if you painted the Diwali sky? (firework colours, Diwali 2026 week)
Facts: firework colours come from metal compounds: strontium red, calcium orange, sodium yellow, barium green,
copper blue, strontium + copper purple (Brock University chart; Mental Floss; The World/PRI 2019).
Heat lifts electrons in the metal atoms to higher levels; when they drop back they give off light at fixed
wavelengths, a fingerprint for each element (ScienceABC). Red and green are the easiest colours, blue is the hardest
(LiveScience expert via Mental Floss); the blue emitter copper(I) chloride falls apart above about 1,200 C
(ScienceABC). Sodium's yellow D-line is 589 nm, the glow of sodium street lamps.
Sivakasi, Tamil Nadu makes over 85% of India's fireworks (Business Standard 2024).
Sparklers burn at about 1,200-3,000 F, i.e. well over 1,000 C (VUMC 2026); keep water nearby, never relight duds (CPSC).
Twist: total solar eclipse of 18 Aug 1868, Pierre Janssen at Guntur, India saw a bright yellow line at 587.5 nm, next to
sodium's D lines; Lockyer and Frankland named it helium after helios; Ramsay found helium on Earth in 1895, 27 years later
(Deccan Herald; hjkc.de)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE = (255, 60, 70), (255, 150, 40), (255, 230, 60), (70, 230, 90), \
    (70, 140, 255), (190, 90, 255)

def burst(d, cx, cy, col, p, r=230, n=26, seed=0):
    """Firework burst, p = seconds since it exploded (loops every 2.2 s)."""
    if p < 0: return
    if p < 0.55:   # rocket climbing
        q = p / 0.55
        y = 1000 - (1000 - cy) * ease_out(q)
        d.line([(cx, y), (cx, y + 70)], fill=(255, 220, 160), width=6)
        d.ellipse([cx - 8, y - 8, cx + 8, y + 8], fill=WHITE)
        return
    t = p - 0.55
    q = ease_out(clamp(t / 1.1))
    fade = 1 - clamp((t - 0.9) / 0.75)
    if fade <= 0: return
    c = tuple(int(v * fade + 30 * (1 - fade)) for v in col)
    rr = r * q
    for k in range(n):
        a = 2 * math.pi * k / n + seed
        sag = 60 * t * t
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a) + sag
        x0, y0 = cx + rr * 0.72 * math.cos(a), cy + rr * 0.72 * math.sin(a) + sag * 0.8
        d.line([(x0, y0), (x, y)], fill=c, width=7)
        s = 9 * fade + 2
        d.ellipse([x - s, y - s, x + s, y + s], fill=tuple(min(255, v + 60) for v in c))
    if t < 0.15:
        s = 60 * (1 - t / 0.15)
        d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=WHITE)

def show(d, T, sc, cols, xs=(540,), cy=600, r=230, period=2.2):
    lt = T - sc["s"] - 0.5
    for i, (col, x) in enumerate(zip(cols, xs)):
        p = (lt - i * 0.45) % period if lt - i * 0.45 >= 0 else -1
        burst(d, x, cy + (i % 2) * 40, col, p, r, seed=i * 0.4)

def metal_props(frame, d, T, sc):
    show(d, T, sc, [(255, 250, 230), RED, GREEN], xs=(540, 260, 820), r=180)
    if T - sc["s"] > 1.0: top_label(frame, "COLOUR = METAL", 380, YEL, 70)

def red_props(frame, d, T, sc):
    show(d, T, sc, [RED, RED], xs=(360, 740), r=220)
    if T - sc["s"] > 1.0: top_label(frame, "RED = STRONTIUM", 380, (255, 120, 120), 68)

def oy_props(frame, d, T, sc):
    show(d, T, sc, [ORANGE, YELLOW], xs=(330, 750), r=210)
    if T - sc["s"] > 1.0: top_label(frame, "CALCIUM + SODIUM", 380, YEL, 64)

def green_props(frame, d, T, sc):
    show(d, T, sc, [GREEN, GREEN, GREEN], xs=(540, 260, 820), r=180)
    if T - sc["s"] > 1.0: top_label(frame, "GREEN = BARIUM", 380, (120, 240, 140), 68)

def blue_props(frame, d, T, sc):
    lt = T - sc["s"]
    # first a proper blue, then an over-heated one that washes out to white
    p = lt - 0.5
    if 0 <= p < 2.6: burst(d, 540, 600, BLUE, p, 240)
    p2 = lt - 3.4
    if p2 >= 0: burst(d, 540, 620, (225, 230, 245), p2 % 2.6, 240, seed=0.3)
    if lt > 1.0: top_label(frame, "BLUE = COPPER (HARDEST)", 380, (140, 180, 255), 58)
    if lt > 3.6:
        l = label("TOO HOT = NO BLUE", 52, WHITE); comp(frame, l, 540 - l.width / 2, 860)

def purple_props(frame, d, T, sc):
    lt = T - sc["s"]
    # red + blue drift together, then a purple burst
    g = ease_out(clamp((lt - 0.4) / 1.4))
    if lt < 2.0:
        for x0, c in ((180, RED), (900, BLUE)):
            x = x0 + (540 - x0) * g
            d.ellipse([x - 70, 560, x + 70, 700], fill=c, outline=OUTL, width=6)
    else:
        burst(d, 540, 600, PURPLE, (lt - 2.0) % 2.4 + 0.55, 250)
    if lt > 1.0: top_label(frame, "RED + BLUE = PURPLE", 380, (210, 150, 255), 64)

def boxes(d, T):
    cols = [(230, 60, 70), (255, 190, 40), (60, 160, 230), (120, 200, 90), (200, 90, 220)]
    k = 0
    for row in range(3):
        for i in range(5 - (row % 2)):
            x = 130 + i * 180 + (90 if row % 2 else 0)
            y = 1130 - row * 120
            c = cols[k % 5]; k += 1
            d.rounded_rectangle([x, y, x + 160, y + 110], radius=10, fill=c, outline=OUTL, width=5)
            d.rectangle([x + 20, y + 40, x + 140, y + 70], fill=(255, 245, 220))

def siva_props(frame, d, T, sc):
    boxes(d, T)
    if T - sc["s"] > 1.0: top_label(frame, "SIVAKASI, TAMIL NADU", 380, YEL, 62)
    if T - sc["s"] > 2.0:
        l = label("OVER 85%", 120, YEL); comp(frame, l, 540 - l.width / 2, 470)

def bucket(d, x=760, y=1120):
    d.polygon([(x - 120, y - 120), (x + 120, y - 120), (x + 95, y + 110), (x - 95, y + 110)],
              fill=(110, 150, 210), outline=OUTL, width=7)
    d.ellipse([x - 120, y - 150, x + 120, y - 90], fill=(90, 190, 240), outline=OUTL, width=7)
    d.arc([x - 120, y - 260, x + 120, y - 20], 190, 350, fill=OUTL, width=8)

def safe_props(frame, d, T, sc):
    bucket(d)
    lt = T - sc["s"]
    # a sparkler: stick + crackling sparks
    sx, sy = 250, 930
    d.line([(250, 1150), (sx, sy)], fill=(130, 130, 140), width=8)
    for k in range(16):
        a = (k * 2.4 + T * 9) % (2 * math.pi)
        rr = 30 + 60 * ((T * 3 + k * 0.37) % 1.0)
        x, y = sx + rr * math.cos(a), sy + rr * math.sin(a)
        d.line([(sx + 0.5 * rr * math.cos(a), sy + 0.5 * rr * math.sin(a)), (x, y)], fill=(255, 230, 150), width=4)
    d.ellipse([sx - 16, sy - 16, sx + 16, sy + 16], fill=WHITE)
    if lt > 1.0: top_label(frame, "OVER 1,000 °C", 380, YEL, 72)

def sun_ring(d, T, cx=540, cy=640):
    # eclipse: black Moon disc with a glowing corona
    for k in range(14):
        a = k * 2 * math.pi / 14 + 0.2 * math.sin(T)
        d.line([(cx + 170 * math.cos(a), cy + 170 * math.sin(a)), (cx + 250 * math.cos(a), cy + 250 * math.sin(a))],
               fill=(255, 230, 160), width=10)
    d.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], fill=(255, 240, 200))
    d.ellipse([cx - 160, cy - 160, cx + 160, cy + 160], fill=(20, 16, 30))

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    sun_ring(d, T)
    if lt > 1.0: top_label(frame, "1868: GUNTUR, INDIA", 380, YEL, 66)

def spectrum(frame, d, T, lt, y=800):
    x0, x1 = 120, 960
    cols = [(150, 60, 220), (60, 90, 240), (40, 200, 230), (60, 220, 90), (250, 230, 50), (255, 150, 40), (240, 50, 50)]
    seg = (x1 - x0) / (len(cols) - 1)
    for i in range(len(cols) - 1):
        for j in range(int(seg)):
            q = j / seg
            c = tuple(int(cols[i][m] * (1 - q) + cols[i + 1][m] * q) for m in range(3))
            x = x0 + i * seg + j
            d.line([(x, y), (x, y + 110)], fill=c, width=2)
    d.rectangle([x0, y, x1, y + 110], outline=OUTL, width=6)
    # sodium's double line and the new helium line just beside it
    xs = 680
    d.line([(xs + 26, y - 10), (xs + 26, y + 120)], fill=OUTL, width=6)
    d.line([(xs + 36, y - 10), (xs + 36, y + 120)], fill=OUTL, width=6)
    if lt > 1.2:
        fl = 3 if int(T * 6) % 2 else 0
        d.line([(xs, y - 30), (xs, y + 140)], fill=WHITE, width=10 + fl)
        l = label("NEW!", 48, WHITE); comp(frame, l, xs - l.width - 40, y + 128)
    ls = label("SODIUM", 40, YEL); comp(frame, ls, xs + 60, y + 130)

def helium_props(frame, d, T, sc):
    lt = T - sc["s"]
    spectrum(frame, d, T, lt)
    if lt > 1.0: top_label(frame, "HELIOS = SUN", 380, YEL, 66)

KID = (540, 1150, 400)

S = [
    dict(id="intro", s=0.0, e=4.5),
    dict(id="metal", s=4.5, e=12.0, bg="diwali", clock="DIWALI NIGHT", char="kid", pos=KID, props=metal_props,
         look=(0, -0.7),
         narr="Every firework colour comes from a burning METAL. Each metal glows its OWN colour.", n_at=4.7),
    dict(id="red", s=12.0, e=19.0, bg="diwali", clock="RED", char="kid", pos=KID, props=red_props, look=(0, -0.7),
         narr="RED is STRONTIUM. Heat kicks its electrons up. Falling back, they GLOW red.", n_at=12.2),
    dict(id="oy", s=19.0, e=26.0, bg="diwali", clock="ORANGE + YELLOW", char="kid", pos=KID, props=oy_props,
         look=(0, -0.7),
         narr="CALCIUM gives ORANGE. SODIUM gives YELLOW, the glow of old street lamps.", n_at=19.2),
    dict(id="green", s=26.0, e=33.0, bg="diwali", clock="GREEN", char="kid", pos=KID, props=green_props,
         look=(0, -0.7),
         narr="GREEN comes from BARIUM. Red and green are the EASIEST colours to make.", n_at=26.2,
         say="EASY mode!", say_at=29.4, pitch=820, bubble_y=780),
    dict(id="blue", s=33.0, e=40.0, bg="diwali", clock="BLUE", char="kid", pos=KID, props=blue_props,
         look=(0, -0.7),
         narr="BLUE is the HARDEST. Its copper compound breaks apart above about 1,200 °C.", n_at=33.2),
    dict(id="purple", s=40.0, e=47.0, bg="diwali", clock="PURPLE", char="kid", pos=KID, props=purple_props,
         look=(0, -0.7),
         narr="Want PURPLE? Mix red STRONTIUM with blue COPPER.", n_at=40.2,
         say="Colour MIXING!", say_at=43.4, pitch=820, bubble_y=780),
    dict(id="siva", s=47.0, e=54.0, bg="sweetshop", clock="MADE IN INDIA", char="diya", pos=(540, 770, 240),
         props=siva_props, look=(0, 0.3),
         narr="Over 85% of India's fireworks are made in ONE town: SIVAKASI.", n_at=47.2),
    dict(id="safe", s=54.0, e=61.0, bg="diwali", clock="SAFETY FIRST", char="kid", pos=(540, 1150, 380),
         props=safe_props, look=(0.5, -0.3),
         narr="A SPARKLER burns over 1,000 °C. Keep a BUCKET of water. Never relight a DUD.", n_at=54.2,
         say="Water BUCKET ready!", say_at=57.4, pitch=820, bubble_y=780),
    dict(id="twist", s=61.0, e=68.0, bg="space", clock="PLOT TWIST", char="kid", pos=(540, 1150, 380),
         props=twist_props, twist=True, look=(0, -0.7),
         narr="Twist: 1868, an ECLIPSE seen from GUNTUR, India. The Sun showed a strange YELLOW line.",
         n_at=61.2),
    dict(id="helium", s=68.0, e=75.5, bg="space", clock="27 YEARS LATER", char="sun", pos=(540, 1150, 260),
         props=helium_props, look=(0, -0.3),
         narr="Not sodium. A NEW element, named after the Sun: HELIUM. Found on Earth 27 YEARS later!",
         n_at=68.2, say="My GAS!", say_at=71.8, pitch=620, bubble_y=690),
    dict(id="outro", s=75.5, e=80.5),
]

def intro_extra(frame, d, T):
    if T >= 1.0:
        for i, (col, x) in enumerate(((RED, 240), (GREEN, 840), (BLUE, 540))):
            burst(d, x, 300 if i < 2 else 260, col, ((T - 1.0 - i * 0.3) % 2.4), 150, seed=i)
    if T >= 2.1:
        p = ease_back(clamp((T - 2.1) / 0.4))
        if p > 0.05: paste_c(frame, E.draw_char("diya", 380, T, 0, False, (0, -0.2), 1), 540, 1480, p)

cfg = dict(
    total=80.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU PAINTED", WHITE)], 140), 760, 0.75, "right"),
        (title([("THE DIWALI", YEL)], 160), 920, 1.05, "pop"),
        (title([("SKY?", WHITE)], 160), 1080, 1.5, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which colour would", WHITE)], 92), 470, 0.15),
                      (title([("YOU", YEL), (" paint?", WHITE)], 110), 600, 0.45)],
               row=[("diya", 1), ("kid", 1), ("sun", 1), ("uncle", 1), ("diya", 1)],
               note=text_sprite([("Light at arm's length. ", WHITE), ("Keep water nearby.", YEL)], 40, stroke=6)),
    music=[dict(t0=0.2, t1=4.5, drums=False), dict(t0=4.5, t1=33.0, melody=True),
           dict(t0=33.0, t1=40.0, drums=False, minor=True), dict(t0=40.0, t1=54.0, melody=True),
           dict(t0=54.0, t1=60.85, drums=False)],
    drones=[dict(t0=61.2, dur=14.0, g=0.05)],
    fx=[("whistle", 5.0, 0.25), ("boom", 5.6, 0.25), ("whistle", 12.5, 0.25), ("boom", 13.1, 0.3),
        ("boom", 13.5, 0.25), ("boom", 19.6, 0.25), ("boom", 20.0, 0.25), ("boom", 26.6, 0.25),
        ("boom", 33.6, 0.3), ("powerdown", 36.2, 0.3), ("ding", 42.6, 0.3), ("boom", 42.6, 0.3),
        ("pop", 49.2, 0.5), ("click", 55.0, 0.4), ("splash", 57.8, 0.4), ("ding", 70.0, 0.4)],
    outro_end=None,
)
cfg.pop("outro_end")
cfg["music"].append(dict(t0=75.5, t1=80.5, melody=True))

if __name__ == "__main__":
    E.main(cfg, "what_if_you_painted_the_diwali_sky")
