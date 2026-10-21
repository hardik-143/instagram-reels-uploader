#!/usr/bin/env python3
"""What if a spoonful of neutron star came to Earth? A giant star's core collapses in a supernova; the neutron
star left behind holds about a Sun's mass in ~20 km (NASA); a sugar cube of it weighs ~1 billion tonnes on Earth
(NASA), more than all humans combined (~390 million tonnes, Sci. Am.); the fastest spins 700+ times a second
(vs ~350 rpm ceiling fan); freed from its gravity a spoonful would blow up in a giant explosion (Astronomy mag).
Twist: much of Earth's gold may have been forged in neutron-star collisions (CfA / GW170817 kilonova)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

BLAST = 48.6   # the spoonful bursts

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

_gl = {}
def glow_spr(r, col, strength=0.8):
    k = (int(r), col, round(strength, 2))
    if k not in _gl:
        R = max(2, int(r))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        q = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / R, 0, 1) ** 2
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (q * 255 * strength).astype(np.uint8)
        _gl[k] = Image.fromarray(arr, "RGBA")
    return _gl[k]

def glow(frame, x, y, r, col=(150, 200, 255), s=0.8):
    g = glow_spr(r, col, s)
    frame.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

# ---------------------------------------------------------------- new character: a tiny, glowing neutron star
def nstar(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))
    def EL(b, fill, w=2.6):
        d.ellipse([v * u for v in b], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    EL((30, 30, 170, 170), (196, 226, 255))
    EL((48, 44, 96, 80), (240, 248, 255), w=0)
    EL((56, 112, 72, 122), (255, 160, 180), w=0); EL((128, 112, 144, 122), (255, 160, 180), w=0)
    for i, x in enumerate((80, 120)):
        r = 13
        if blink or (state == "wink" and i == 1):
            d.arc([(x - r) * u, (96 - r * 0.7) * u, (x + r) * u, (96 + r * 0.7) * u], 200, 340, fill=OUTL, width=lw(3))
            continue
        EL((x - r, 96 - r * 1.1, x + r, 96 + r * 1.1), WHITE, w=2.2)
        px, py = x + look[0] * 5, 96 + look[1] * 5
        EL((px - 6, py - 7, px + 6, py + 7), (25, 20, 30), w=0)
        EL((px - 5, py - 6, px - 1, py - 2), WHITE, w=0)
    if talk > 0.08:
        EL((90, 122, 110, 128 + 14 * talk), (125, 28, 48), w=1.8)
    else:
        d.arc([86 * u, 114 * u, 114 * u, 134 * u], 20, 160, fill=OUTL, width=lw(2.6))
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "nstar":
        return nstar(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char   # the engine looks the name up at render time

# ---------------------------------------------------------------- props
def death_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 3.2:
        q = ease_out(clamp((lt - 3.2) / 2.5))
        r = 120 + 560 * q
        c = (255, int(200 - 80 * q), int(120 - 80 * q))
        d.ellipse([540 - r, 1060 - r, 540 + r, 1060 + r], outline=c, width=int(26 * (1 - q)) + 4)

def death_overlay(frame, T, sc):
    lt = T - sc["s"]
    if 3.2 <= lt < 3.6:
        return Image.blend(frame, Image.new("RGBA", (W, H), (255, 240, 220, 255)), 0.7 * (1 - (lt - 3.2) / 0.4))
    return frame

def city(d, y=1320):
    xs = [(70, 170, 250), (180, 260, 330), (270, 380, 200), (390, 470, 290), (480, 580, 230), (590, 660, 340),
          (670, 780, 260), (790, 870, 300), (880, 1010, 210)]
    for x0, x1, h in xs:
        d.rectangle([x0, y - h, x1, y], fill=(40, 46, 90))
        for wy in range(y - h + 20, y - 10, 36):
            for wx in range(x0 + 12, x1 - 12, 26):
                d.rectangle([wx, wy, wx + 10, wy + 14], fill=(255, 220, 120))

def born_props(frame, d, T, sc):
    lt = T - sc["s"]
    glow(frame, 540, 1010, 260, (140, 190, 255), 0.8)
    city(d, 1330)
    if lt > 1.0:
        q = ease_out(clamp((lt - 1.0) / 0.8))
        x0, x1 = 540 - 400 * q, 540 + 400 * q
        d.line([(x0, 1360), (x1, 1360)], fill=YEL, width=8)
        d.line([(x0, 1340), (x0, 1380)], fill=YEL, width=8); d.line([(x1, 1340), (x1, 1380)], fill=YEL, width=8)
    if lt > 1.8:
        top_label(frame, "~20 KM WIDE", 380, YEL, 76)

def sugar_cube(frame, d, x, y, s, T):
    glow(frame, x, y, 150 * s, (150, 210, 255), 0.9)
    h = 46 * s
    d.polygon([(x - h, y - h * 0.4), (x, y - h * 0.9), (x + h, y - h * 0.4), (x, y + h * 0.1)], fill=(250, 252, 255), outline=OUTL)
    d.polygon([(x - h, y - h * 0.4), (x, y + h * 0.1), (x, y + h * 1.1), (x - h, y + h * 0.6)], fill=(214, 230, 250), outline=OUTL)
    d.polygon([(x + h, y - h * 0.4), (x, y + h * 0.1), (x, y + h * 1.1), (x + h, y + h * 0.6)], fill=(186, 208, 240), outline=OUTL)

def cube_props(frame, d, T, sc):
    lt = T - sc["s"]
    # counter cracks under the cube
    sugar_cube(frame, d, 300, 1150, 1.9, T)
    if lt > 2.0:
        for k in range(5):
            a = -0.4 + k * 0.2
            d.line([(300, 1250), (300 + 220 * math.cos(math.pi / 2 + a * 3), 1250 + 90 * abs(math.sin(a * 3)) + 20)],
                   fill=OUTL, width=5)
    if lt > 0.8:
        top_label(frame, "1 BILLION TONNES", 380, YEL, 76)

def head(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=OUTL, width=3)

def humans_props(frame, d, T, sc):
    lt = T - sc["s"]
    tilt = 0.32 * ease_out(clamp((lt - 0.8) / 1.2))       # cube side goes down
    cx, cy, L = 540, 1000, 430
    lx, ly = cx - L * math.cos(tilt), cy + L * math.sin(tilt)
    rx, ry = cx + L * math.cos(tilt), cy - L * math.sin(tilt)
    d.polygon([(cx - 60, 1170), (cx + 60, 1170), (cx, cy + 10)], fill=(150, 100, 70), outline=OUTL)
    d.line([(lx, ly), (rx, ry)], fill=(120, 80, 50), width=22)
    sugar_cube(frame, d, lx + 40, ly - 50, 0.8, T)
    skins = [(242, 194, 152), (226, 168, 118), (190, 130, 90), (160, 104, 70)]
    for k in range(26):
        row, colm = divmod(k, 7)
        x = rx - 260 + colm * 42 + row * 18 - 30
        y = ry - 34 - row * 40 + (x - rx) * math.tan(tilt) * -1
        head(d, x, y, 22, skins[k % 4])
    if lt > 1.4:
        l1 = label("1 CUBE", 54, YEL); comp(frame, l1, lx - l1.width / 2 + 40, ly + 40)
        l2 = label("ALL HUMANS", 54, WHITE); comp(frame, l2, rx - l2.width / 2 - 120, ry - 300)

def beams(frame, d, T, cx, cy, spin=3.0, L=700):
    a = T * spin
    for s in (0, math.pi):
        ex, ey = cx + L * math.cos(a + s), cy + L * math.sin(a + s) * 0.45
        w1 = 44
        nx, ny = -math.sin(a + s) * w1, math.cos(a + s) * w1 * 0.45
        d.polygon([(cx, cy), (ex + nx, ey + ny), (ex - nx, ey - ny)], fill=(200, 230, 255))

def spin_props(frame, d, T, sc):
    lt = T - sc["s"]
    glow(frame, 540, 1000, 300, (140, 190, 255), 0.7)
    beams(frame, d, T, 540, 1000, spin=9.0)
    if lt > 0.8:
        top_label(frame, "700+ SPINS A SECOND", 380, YEL, 68)

def spoon(frame, d, x, y, T):
    d.line([(x + 30, y + 20), (x + 260, y - 160)], fill=(190, 196, 210), width=26)
    d.line([(x + 30, y + 20), (x + 260, y - 160)], fill=OUTL, width=4)
    d.ellipse([x - 80, y - 40, x + 60, y + 60], fill=(210, 216, 228), outline=OUTL, width=6)
    glow(frame, x - 10, y + 6, 120, (150, 210, 255), 0.9)
    d.ellipse([x - 44, y - 18, x + 24, y + 34], fill=(220, 238, 255), outline=OUTL, width=4)

def spoon_props(frame, d, T, sc):
    lt = T - sc["s"]
    y = 560 + 520 * ease_out(clamp(lt / 2.0))
    spoon(frame, d, 360, y, T)

def boom_props(frame, d, T, sc):
    lt = T - BLAST
    if lt < 0:
        spoon(frame, d, 360, 1080 + 6 * math.sin(T * 40), T)

def boom_overlay(frame, T, sc):
    lt = T - BLAST
    if lt < 0: return frame
    q = clamp(lt / 0.5)
    f = Image.blend(frame, Image.new("RGBA", (W, H), (255, 250, 235, 255)), 0.85 * (1 - clamp((lt - 0.5) / 2.0)))
    if q < 1:
        f = Image.blend(frame, Image.new("RGBA", (W, H), (255, 250, 235, 255)), 0.85 * q)
    return f

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    q = clamp(lt / 3.0)
    r = 300 * (1 - q) + 10
    a = lt * (2 + 10 * q)
    for s in (0, math.pi):
        x, y = 540 + r * math.cos(a + s), 1060 + r * 0.5 * math.sin(a + s)
        glow(frame, x, y, 90, (150, 200, 255), 0.9)
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=(220, 236, 255), outline=OUTL, width=4)
    if lt > 3.0:
        glow(frame, 540, 1060, 260 + 60 * math.sin(T * 6), (255, 200, 80), 0.9)
        for k in range(16):
            ph = ((lt - 3.0) * 0.6 + k / 16) % 1.0
            ang = k * 2.4
            x, y = 540 + 520 * ph * math.cos(ang), 1060 + 420 * ph * math.sin(ang)
            d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(255, 205, 60), outline=OUTL, width=3)
        top_label(frame, "GOLD!", 380, YEL, 96)

def coin(d, x, y, r=34):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 200, 50), outline=OUTL, width=4)
    d.ellipse([x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6], outline=(200, 140, 20), width=4)

def gold_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(10):
        ph = (lt * 0.35 + k / 10) % 1.0
        x = 120 + (k * 211) % 860
        coin(d, x, 380 + 900 * ph)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="death", s=4.0, e=11.0, bg="space", clock="A GIANT STAR DIES", char="sun", pos=(540, 1060, 520),
         props=death_props, overlay=death_overlay, look=(0, 0),
         narr="When a GIANT star dies, it EXPLODES and its core gets crushed.", n_at=4.2, narr_y=1500,
         say="Going out with a BANG!", say_at=5.0, pitch=200),
    dict(id="born", s=11.0, e=18.0, bg="space", clock="NEUTRON STAR", char="nstar", pos=(540, 1010, 260),
         props=born_props, look=(0, 0.5),
         narr="Left behind: a NEUTRON STAR. About a Sun's mass, only 20 KM wide.", n_at=11.2, narr_y=1530,
         say="Small but MIGHTY!", say_at=14.2, pitch=520),
    dict(id="cube", s=18.0, e=25.0, bg="cat", clock="ONE SUGAR CUBE", char="chai", pos=(740, 1100, 420),
         props=cube_props, look=(-0.6, 0.3),
         narr="One SUGAR CUBE of it would weigh about 1 BILLION TONNES on Earth.", n_at=18.2, narr_y=1500,
         say="Make mine NO sugar!", say_at=21.4, pitch=360),
    dict(id="humans", s=25.0, e=32.0, bg="day", clock="WEIGH-IN", props=humans_props,
         narr="That's heavier than ALL 8 BILLION humans put together!", n_at=25.2, narr_y=1500),
    dict(id="spin", s=32.0, e=39.0, bg="space", clock="SPIN CYCLE", char="nstar", pos=(540, 1000, 300),
         props=spin_props, look=(0.3, -0.3),
         narr="Some spin over 700 TIMES a second, 100x faster than a ceiling fan!", n_at=32.2, narr_y=1500,
         say="Wheee! I'm DIZZY!", say_at=35.2, pitch=560),
    dict(id="spoon", s=39.0, e=46.0, bg="cat", clock="SPECIAL DELIVERY", char="kid", pos=(760, 1100, 420),
         props=spoon_props, look=(-0.6, -0.2),
         narr="So what if one SPOONFUL of it landed in your kitchen?", n_at=39.2, narr_y=1500,
         say="Ooh, SHINY!", say_at=42.4, pitch=420),
    dict(id="boom", s=46.0, e=53.0, bg="cat", clock="UH-OH", char="uncle", state="angry", pos=(760, 1100, 420),
         props=boom_props, overlay=boom_overlay, look=(-0.6, 0),
         narr="Freed from the star's crushing GRAVITY, it would burst in a GIANT explosion.", n_at=46.2, narr_y=1500,
         say="WHO ordered THIS?!", say_at=46.8, pitch=150),
    dict(id="twist", s=53.0, e=60.0, bg="twist", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: much of Earth's GOLD may have been forged when neutron stars COLLIDED.", n_at=53.2, narr_y=1500),
    dict(id="gold", s=60.0, e=67.0, bg="diwali", clock="DHANTERAS", char="diya", state="wink", pos=(540, 1060, 440),
         props=gold_props, look=(0, 0),
         narr="So that DHANTERAS gold coin? It might be COLLIDING-STAR stuff!", n_at=60.2, narr_y=1500,
         say="Shiny AND cosmic!", say_at=63.2, pitch=420),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        y = 1440 + 14 * math.sin(T * 3)
        p = ease_back((T - 1.9) / 0.4)
        if p > 0.05:
            spoon(frame, d, 470, y, T)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("A SPOONFUL OF", WHITE)], 120), 760, 0.75, "right"),
        (title([("NEUTRON STAR", WHITE)], 130), 900, 1.05, "left"),
        (title([("...", WHITE), ("HIT EARTH?", YEL)], 100), 1050, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" hold", WHITE)], 100), 470, 0.15),
                      (title([("a spoonful?", YEL)], 116), 600, 0.45)],
               row=[("nstar", 1), ("sun", 1), ("chai", 1), ("diya", 1), ("nstar", "wink")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, drums=False, minor=True),
           dict(t0=11.0, t1=39.0, melody=True), dict(t0=39.0, t1=46.0), dict(t0=46.0, t1=52.85, drums=False, minor=True),
           dict(t0=60.0, t1=72.0, melody=True)],
    drones=[dict(t0=4.0, dur=14.0, g=0.4)],
    fx=[("boom", 7.2, 0.9), ("rumble", 7.3, 0.4, dict(dd=3.5)), ("crash", 22.0, 0.5), ("whoosh", 32.4, 0.6),
        ("whoosh", 33.6, 0.5), ("whoosh", 39.2, 0.8), ("boom", BLAST, 1.0), ("rumble", BLAST + 0.1, 0.5, dict(dd=4.0)),
        ("boom", 56.2, 0.7), ("ding", 57.0, 0.4), ("pop", 61.0, 0.4), ("pop", 62.0, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_a_spoonful_of_neutron_star")
