#!/usr/bin/env python3
"""What if Earth had rings like Saturn? Facts: Saturn's main rings span about 273,600 km (170,000 miles) and are
about 10 m (30 ft) thick (space.com, 'Saturn's rings will disappear this weekend', 2025); mostly water ice with some
rock and dust, chunks from dust up to building/house size (NASA GSFC 'The Rings of Saturn'). Rings form when a body
passes inside a planet's Roche limit and is torn apart by tides (Monash University 2024 press release on Tomkins et
al., EPSL). Geometry: rings lie in the equatorial plane, so from the northern hemisphere (India) they would arch
across the southern sky, higher near the equator (Kanyakumari ~8 deg N) and appearing edge-on as a thin line from the
equator itself (general astronomy; stated as a hypothetical). Ring shadow would fall on the winter hemisphere; Monash
researchers speculate an ancient ring shading Earth may have contributed to the Hirnantian Icehouse (hypothesis).
Saturn's rings 'vanished' edge-on on 23 March 2025 (ring-plane crossing; space.com). Twist: Monash 2024 study
suggests Earth may have had a ring ~466 million years ago, from 21 Ordovician craters all within 30 deg of the
equator; first dinosaurs appeared ~230 million years ago. Saturn (Shani) reached opposition 4 Oct 2026
(BusinessToday citing NASA), so it is in the November evening sky (caption only)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
RING = [(236, 214, 170), (210, 186, 140), (246, 230, 196), (196, 170, 128)]
SAT = (232, 196, 128)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def put(frame, txt, cx, y, size=52, col=WHITE):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def ring_layer(cx, cy, R, flat, half, alpha=255):
    """Ring band as an RGBA layer. half: 'back' (top half) or 'front' (bottom half)."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    start, end = (180, 360) if half == "back" else (0, 180)
    n = len(RING)
    for i in range(n):
        r = R * (1.0 - i * 0.11)
        ry = max(1.5, r * flat)
        col = RING[i] + (alpha,)
        d.arc([cx - r, cy - ry, cx + r, cy + ry], start, end, fill=OUTL + (alpha,), width=int(max(4, R * 0.1)) + 4)
    for i in range(n):
        r = R * (1.0 - i * 0.11)
        ry = max(1.5, r * flat)
        d.arc([cx - r, cy - ry, cx + r, cy + ry], start, end, fill=RING[i] + (alpha,), width=int(max(3, R * 0.1)))
    return L

def saturn(frame, d, cx, cy, r, flat=0.28, tilt=-14):
    big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    big.alpha_composite(ring_layer(cx, cy, r * 2.1, flat, "back"))
    bd = ImageDraw.Draw(big)
    bd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SAT, outline=OUTL, width=8)
    for k in (-0.45, -0.1, 0.3):
        yy = cy + k * r
        hw = math.sqrt(max(0, r * r - (yy - cy) ** 2))
        bd.line([(cx - hw + 10, yy), (cx + hw - 10, yy)], fill=(206, 164, 98), width=int(r * 0.12))
    big.alpha_composite(ring_layer(cx, cy, r * 2.1, flat, "front"))
    big = big.rotate(tilt, center=(cx, cy), resample=Image.BICUBIC)
    frame.alpha_composite(big)

def ringed_earth(frame, T, cx, cy, size, flat=0.26, tilt=-18, alpha=255, rscale=2.0):
    big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    big.alpha_composite(ring_layer(cx, cy, size * 0.5 * rscale, flat, "back", alpha))
    spr = draw_char("earth", int(size), T, 0, False, (0, 0.2), T * 0.2)
    big.alpha_composite(spr, (int(cx - size / 2), int(cy - size / 2)))
    big.alpha_composite(ring_layer(cx, cy, size * 0.5 * rscale, flat, "front", alpha))
    if tilt: big = big.rotate(tilt, center=(cx, cy), resample=Image.BICUBIC)
    frame.alpha_composite(big)

# ---------------------------------------------------------------- props
def saturn_props(frame, d, T, sc):
    lt = T - sc["s"]
    saturn(frame, d, 540, 1000, 170 + 6 * math.sin(T * 1.5))
    if lt > 0.5: top_label(frame, "270,000 KM WIDE", 380, YEL, 84)
    if lt > 3.0: put(frame, "BUT ~10 M THICK", 540, 1270, 60, WHITE)

def ice_props(frame, d, T, sc):
    lt = T - sc["s"]
    rng = np.random.default_rng(3)
    for k in range(26):
        x = (rng.uniform(0, 1200) + lt * rng.uniform(30, 90)) % 1200 - 60
        y = rng.uniform(470, 1330)
        s = rng.uniform(10, 70) if k % 6 else rng.uniform(80, 120)
        pts = [(x + s * math.cos(a) * (0.75 + 0.25 * math.sin(a * 3 + k)), y + s * math.sin(a) * 0.8)
               for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
        d.polygon(pts, fill=(222, 238, 250), outline=OUTL)
        d.line([pts[0], pts[3]], fill=(180, 210, 236), width=3)
    if lt > 0.5: top_label(frame, "MOSTLY WATER ICE", 380, YEL, 84)

def torn_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1000
    mini(frame, "earth", cx, cy, 300, T, state=T * 0.2)
    rng = np.random.default_rng(8)
    if lt < 2.8:
        p = ease_out(lt / 2.8)
        x, y = 1000 - 380 * p, 560 + 260 * p
        d.ellipse([x - 50, y - 40, x + 50, y + 40], fill=(150, 130, 115), outline=OUTL, width=6)
        d.ellipse([x - 20, y - 15, x, y + 3], fill=(120, 100, 90))
    else:
        g = clamp((lt - 2.8) / 3.0)
        for k in range(70):
            a0 = math.atan2(820 - cy, 620 - cx)
            a = a0 + g * (k / 70.0) * 2 * math.pi * 1.0 + rng.uniform(-0.1, 0.1) * (1 - g)
            rr = 250 + rng.uniform(-20, 20) + (1 - g) * 40
            x, y = cx + rr * math.cos(a), cy + rr * 0.32 * math.sin(a)
            s = rng.uniform(5, 12)
            d.ellipse([x - s, y - s, x + s, y + s], fill=(170, 150, 130), outline=OUTL)
    if lt > 0.5: top_label(frame, "TORN APART", 380, YEL, 96)

def sky_bg(T):
    img = E.bg("night").copy()
    return img

def horizon(d, y=1210):
    d.rectangle([0, y, W, H], fill=(30, 40, 60))
    xs = [0, 80, 80, 200, 200, 260, 260, 400, 400, 470, 470, 620, 620, 700, 700, 860, 860, 940, 940, 1080]
    hs = [60, 60, 130, 130, 90, 90, 170, 170, 70, 70, 120, 120, 200, 200, 100, 100, 150, 150, 80, 80]
    pts = [(0, y)] + [(x, y - h) for x, h in zip(xs, hs)] + [(W, y)]
    d.polygon(pts, fill=(26, 30, 48), outline=OUTL)
    for k in range(14):
        x = 30 + k * 76
        d.rectangle([x, y - 40, x + 14, y - 26], fill=(255, 214, 110))

def sky_arch(frame, cx, top, half_w, base, thick=70, alpha=235):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
    h = base - top
    if h < thick + 10: return
    for i, col in enumerate(RING):
        off = i * thick / len(RING)
        dd.arc([cx - half_w + off, top + off, cx + half_w - off, base + h - off], 180, 360,
               fill=col + (alpha,), width=int(thick / len(RING)) + 2)
    frame.alpha_composite(L)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp(lt / 1.5))
    sky_arch(frame, 540, 1210 - 470 * g, 640, 1210, 90)
    horizon(d)
    put(frame, "SOUTH", 540, 1225, 48, (200, 210, 240))
    if lt > 0.5: top_label(frame, "VIEW FROM INDIA", 380, YEL, 86)

def equator_props(frame, d, T, sc):
    lt = T - sc["s"]
    # left panel: Kanyakumari, high arch; right panel: equator, thin line
    d.line([(540, 470), (540, 1210)], fill=WHITE, width=6)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sky_arch(L, 270, 520, 300, 1210, 60)
    frame.alpha_composite(L.crop((0, 0, 536, H)), (0, 0))
    yy = 560 + 6 * math.sin(T * 2)
    d.line([(560, yy), (1060, yy)], fill=OUTL, width=12)
    d.line([(560, yy), (1060, yy)], fill=RING[0], width=6)
    horizon(d)
    put(frame, "OVERHEAD", 810, yy + 30, 44, WHITE)
    put(frame, "KANYAKUMARI", 270, 1225, 46, YEL)
    put(frame, "EQUATOR", 810, 1225, 46, YEL)
    if lt > 0.5: top_label(frame, "HIGHER IN THE SOUTH", 380, YEL, 78)

def shadow_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, S = 560, 1060, 340
    ringed_earth(frame, T, cx, cy, S, flat=0.22, tilt=-20, rscale=2.2)
    # shadow band over the southern (winter) half
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(L)
    g = clamp(lt / 1.5)
    sd.chord([cx - S / 2 + 10, cy - S / 2 + 10, cx + S / 2 - 10, cy + S / 2 - 10], 20, 120,
             fill=(10, 10, 30, int(150 * g)))
    frame.alpha_composite(L)
    # sun on the left
    d.ellipse([20, 880, 140, 1000], fill=(255, 210, 80), outline=OUTL, width=6)
    if lt > 0.5: top_label(frame, "RING SHADOW", 380, YEL, 92)
    if lt > 1.5: put(frame, "WINTER SIDE", cx + 120, cy + 230, 50, (190, 210, 255))

def edge_props(frame, d, T, sc):
    lt = T - sc["s"]
    f = 0.30 * (1 - ease_out(clamp((lt - 1.0) / 3.0))) + 0.012
    saturn(frame, d, 540, 1000, 160, flat=f, tilt=0)
    if lt > 0.5: top_label(frame, "MARCH 2025", 380, YEL, 92)
    if lt > 4.2: put(frame, "RINGS: GONE?!", 540, 1250, 60, YEL)

def ancient_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 700, 1040
    ringed_earth(frame, T, cx, cy, 300, flat=0.2, tilt=-10, alpha=200, rscale=2.0)
    if lt > 0.5: top_label(frame, "466 MILLION YEARS AGO", 380, YEL, 72)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="saturn", s=4.0, e=11.0, bg="space", clock="SATURN", props=saturn_props,
         narr="Saturn's rings stretch about 270,000 KM, yet are often just 10 METRES thick.", n_at=4.2,
         narr_y=1560),
    dict(id="ice", s=11.0, e=18.0, bg="space", clock="UP CLOSE", props=ice_props, char="kid", pos=(540, 1080, 340),
         look=(0.3, -0.2),
         narr="They're mostly WATER ICE: bits from dust size up to as big as a HOUSE.", n_at=11.2,
         narr_y=1560, say="A giant space GOLA!", say_at=14.4, pitch=440),
    dict(id="torn", s=18.0, e=25.0, bg="space", clock="STEP 1", props=torn_props,
         narr="To get rings, a space rock must come so close that Earth's gravity RIPS it apart.",
         n_at=18.2, narr_y=1560),
    dict(id="india", s=25.0, e=32.0, bg="night", clock="NIGHT SKY", props=india_props,
         narr="From INDIA, a giant glowing arch would cross the SOUTHERN sky, every night.", n_at=25.2,
         narr_y=1590),
    dict(id="equator", s=32.0, e=39.0, bg="night", clock="GO SOUTH", props=equator_props,
         narr="In KANYAKUMARI it climbs almost overhead. On the EQUATOR it's just a thin LINE.",
         n_at=32.2, narr_y=1590),
    dict(id="shadow", s=39.0, e=46.0, bg="space", clock="WINTER", props=shadow_props, char="uncle",
         pos=(200, 1250, 280), look=(0.5, -0.3),
         narr="The rings' SHADOW would fall on the winter half of Earth, making winters COLDER.",
         n_at=39.2, narr_y=1590, say="Shawl season ALL winter?!", say_at=42.4, pitch=150),
    dict(id="edge", s=46.0, e=TW, bg="space", clock="REAL LIFE", props=edge_props,
         narr="Edge-on, thin rings almost VANISH. Saturn's 'disappeared' from our view in MARCH 2025.",
         n_at=46.2, narr_y=1560),
    dict(id="twist", s=TW, e=60.0, bg="space", clock="PLOT TWIST", char="uncle", state="hat",
         pos=(260, 1150, 340), props=ancient_props, twist=True, look=(0.6, 0),
         narr="Twist: scientists think Earth may have HAD a ring, 466 MILLION years ago, before dinosaurs.",
         n_at=TW + 0.2, narr_y=1580, say="So we LOST our rings?!", say_at=TW + 3.2, pitch=150),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        sz = 260 * p
        if sz > 4:
            ringed_earth(frame, T, 540, 1390 + 12 * math.sin(T * 2), sz, flat=0.25, tilt=-14)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EARTH HAD RINGS", WHITE)], 110), 770, 0.75, "right"),
        (title([("LIKE SATURN?", YEL)], 150), 900, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" want", WHITE)], 100), 470, 0.15),
                      (title([("rings in your sky?", YEL)], 96), 600, 0.45)],
               row=[("earth", 1), ("moon", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=25.0, dur=7.0, g=0.18)],
    fx=[("whoosh", 4.5, 0.3), ("pop", 11.6, 0.25), ("pop", 12.4, 0.25), ("rumble", 20.8, 0.3, dict(dd=3.0)),
        ("crash", 20.9, 0.2), ("wind", 25.4, 0.2, dict(dd=6.0)), ("whoosh", 32.5, 0.3),
        ("wind", 39.4, 0.25, dict(dd=6.0)), ("whoosh", 47.5, 0.25), ("pop", 50.3, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_earth_had_rings")
