#!/usr/bin/env python3
"""What if you squeezed a pencil into a diamond? Facts: pencil 'lead' is a mixture of graphite and clay, not metallic
lead (McGill Office for Science and Society). Graphite and diamond are both pure carbon, in different arrangements
(Lavoisier showed diamond is carbon in 1772, IFLScience). Natural diamonds form about 200 km down at about 50,000
times surface pressure and about 1,600 °C, and reach the surface in kimberlite eruptions (ASU Ask an Expert). Diamonds
mined before 1725 came only from India; Brazil was found in 1725 (Sotheby's, Golconda). About 90% of the world's
diamond cutting and polishing happens in Surat (Israel Diamond Institute, Eastern Eye). GE's H. Tracy Hall made the
first reproducible synthetic diamond on 16 Dec 1954 at about 100,000 atmospheres and 1,600 °C (ASME landmark).
Twist: diamond burns in open air at roughly 850-1,000 °C and becomes carbon dioxide gas (MEL Science; Tennant 1797)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
GRAY = (70, 72, 82)
ICE = (190, 236, 255)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def diamond(d, cx, cy, r, glow=0.0, col=ICE):
    """A cut gem seen from the side: table, crown and pointed pavilion."""
    if r < 3: return
    top = cy - r * 0.55; girdle = cy - r * 0.15; tip = cy + r * 0.85
    pts = [(cx - r * 0.55, top), (cx + r * 0.55, top), (cx + r, girdle), (cx, tip), (cx - r, girdle)]
    if glow > 0:
        g = r * (1.0 + 0.45 * glow)
        for a in range(0, 360, 45):
            ra = math.radians(a)
            ln = g if a % 90 == 0 else g * 0.75
            d.line([(cx + math.cos(ra) * r * 0.9, cy + math.sin(ra) * r * 0.9),
                    (cx + math.cos(ra) * ln, cy + math.sin(ra) * ln)], fill=(255, 250, 200), width=max(2, int(r / 12)))
    d.polygon(pts, fill=col, outline=OUTL, width=max(2, int(r / 14)))
    lw = max(2, int(r / 22))
    d.line([(cx - r, girdle), (cx + r, girdle)], fill=OUTL, width=lw)
    for a, b in (((cx - r * 0.55, top), (cx - r * 0.3, girdle)), ((cx + r * 0.55, top), (cx + r * 0.3, girdle)),
                 ((cx - r * 0.3, girdle), (cx, tip)), ((cx + r * 0.3, girdle), (cx, tip)),
                 ((cx - r * 0.3, girdle), (cx, top)), ((cx + r * 0.3, girdle), (cx, top))):
        d.line([a, b], fill=(110, 170, 210), width=lw)
    d.polygon([(cx - r * 0.45, top + r * 0.06), (cx - r * 0.2, top + r * 0.06), (cx - r * 0.55, girdle - r * 0.04)],
              fill=WHITE)

def pencil(d, x0, y0, x1, y1, w=46):
    """Yellow pencil from (x0,y0) eraser end to (x1,y1) tip."""
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    def P(t, s): return (x0 + ux * t + nx * s, y0 + uy * t + ny * s)
    body = L * 0.78
    d.polygon([P(0, -w / 2), P(L * 0.12, -w / 2), P(L * 0.12, w / 2), P(0, w / 2)], fill=(240, 130, 150), outline=OUTL)
    d.polygon([P(L * 0.12, -w / 2), P(L * 0.16, -w / 2), P(L * 0.16, w / 2), P(L * 0.12, w / 2)], fill=(190, 190, 200),
              outline=OUTL)
    d.polygon([P(L * 0.16, -w / 2), P(body, -w / 2), P(body, w / 2), P(L * 0.16, w / 2)], fill=(255, 200, 40),
              outline=OUTL)
    d.polygon([P(body, -w / 2), P(L, 0), P(body, w / 2)], fill=(240, 205, 160), outline=OUTL)
    d.polygon([P(L * 0.93, -w * 0.14), P(L, 0), P(L * 0.93, w * 0.14)], fill=GRAY)
    for k in range(3):
        a, b = P(L * 0.16, (k - 1) * w / 3), P(body, (k - 1) * w / 3)
        d.line([a, b], fill=OUTL, width=3)

# ---------------------------------------------------------------- props
def lead_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp((lt - 0.2) / 0.5))
    pencil(d, 580 + 400 * (1 - p), 1230, 960 + 400 * (1 - p), 1060, 60)
    if lt > 1.0:
        for i, (lab, col) in enumerate((("GRAPHITE", WHITE), ("+ CLAY", (240, 200, 160)))):
            l = label(lab, 58, col); comp(frame, l, 800 - l.width / 2, 850 + i * 66)
    if lt > 0.5:
        top_label(frame, "NOT LEAD!", 380, YEL, 90)

def atoms_props(frame, d, T, sc):
    lt = T - sc["s"]
    # left: graphite as flat sliding sheets
    for row in range(4):
        y = 1000 + row * 70
        sh = 18 * math.sin(T * 2 + row) if lt > 1 else 0
        for k in range(5):
            x = 120 + k * 70 + sh
            d.line([(x, y), (x + 70, y)], fill=(200, 200, 215), width=8)
            d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(150, 150, 165), outline=OUTL, width=4)
    l = label("SOFT SHEETS", 46, WHITE); comp(frame, l, 270 - l.width / 2, 1290)
    # right: diamond as a locked 3D grid
    if lt > 1.6:
        q = ease_back(clamp((lt - 1.6) / 0.5))
        cx, cy = 790, 1110
        pts = []
        for i in range(3):
            for j in range(3):
                pts.append((cx + (i - 1) * 95 * q + (j - 1) * 40 * q, cy + (j - 1) * 90 * q - (i - 1) * 25 * q))
        for a in range(len(pts)):
            for b in range(a + 1, len(pts)):
                if math.dist(pts[a], pts[b]) < 120 * max(q, 0.1):
                    d.line([pts[a], pts[b]], fill=(110, 200, 240), width=6)
        for x, y in pts:
            r = 22 * q
            d.ellipse([x - r, y - r, x + r, y + r], fill=ICE, outline=OUTL, width=4)
        l = label("LOCKED GRID", 46, ICE); comp(frame, l, 790 - l.width / 2, 1290)
    if lt > 0.5:
        top_label(frame, "SAME CARBON", 380, YEL, 84)

def gauge(d, cx, cy, r, frac):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=OUTL, width=8)
    d.arc([cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18], 150, 300, fill=(120, 200, 120), width=14)
    d.arc([cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18], 300, 390, fill=(230, 50, 50), width=14)
    a = math.radians(150 + 240 * frac)
    d.line([(cx, cy), (cx + math.cos(a) * r * 0.75, cy + math.sin(a) * r * 0.75)], fill=OUTL, width=10)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=OUTL)

def squeeze_props(frame, d, T, sc):
    lt = T - sc["s"]
    shake = 6 * math.sin(T * 60) if lt > 1.5 else 0
    frac = clamp(lt / 3.5) * 0.98 + (0.02 * math.sin(T * 30) if lt > 3.5 else 0)
    gauge(d, 820 + shake, 1000, 130, frac)
    if lt > 0.5:
        n = int(50000 * clamp((lt - 0.5) / 3.0))
        top_label(frame, f"{n:,} x AIR PRESSURE", 380, YEL, 70)

def squeeze_after(frame, d, T, sc):
    lt = T - sc["s"]
    shake = 5 * math.sin(T * 55) if lt > 1.0 else 0
    pencil(d, 230 + shake, 1300, 470 + shake, 1300, 40)

def earth_props(frame, d, T, sc):
    lt = T - sc["s"]
    # cross-section of the ground: grass, crust, mantle
    d.rectangle([0, 560, W, 640], fill=(110, 190, 90), outline=OUTL, width=6)
    d.rectangle([0, 640, W, 960], fill=(170, 120, 80))
    d.rectangle([0, 960, W, 1700], fill=(230, 110, 50))
    for k in range(9):
        y = 990 + k * 80
        d.arc([-200 + (k % 2) * 80, y, W + 200, y + 160], 200, 340, fill=(250, 150, 60), width=8)
    # depth ruler
    d.line([(110, 640), (110, 1340)], fill=WHITE, width=8)
    for k, txt in enumerate(("0 KM", "200 KM")):
        l = label(txt, 46, WHITE); comp(frame, l, 140, 610 + k * 700)
    # diamond born deep, then a kimberlite pipe blasts it up
    up = ease_out(clamp((lt - 3.0) / 1.8))
    if lt > 2.6:
        d.polygon([(600, 640), (700, 640), (720, 1360), (580, 1360)], fill=(120, 70, 70), outline=OUTL)
    diamond(d, 650, 1330 - 700 * up, 48, glow=0.6 if lt > 1.0 else 0)
    if lt > 0.5:
        top_label(frame, "200 KM DOWN", 380, YEL, 86)

def river(d, T):
    pts = [(0, 1250), (200, 1200), (400, 1260), (600, 1190), (800, 1240), (1080, 1180)]
    for w, col in ((90, OUTL), (78, (90, 170, 230))):
        d.line(pts, fill=col, width=w, joint="curve")
    for k in range(6):
        x = (T * 120 + k * 190) % W
        d.line([(x, 1220), (x + 40, 1220)], fill=WHITE, width=5)

def golconda_props(frame, d, T, sc):
    lt = T - sc["s"]
    # fort silhouette on a hill + river with sparkles
    d.polygon([(560, 1060), (1080, 1060), (1080, 1180), (480, 1180)], fill=(150, 120, 90), outline=OUTL)
    for x in (620, 760, 900, 1020):
        d.rectangle([x, 960, x + 70, 1070], fill=(200, 160, 110), outline=OUTL, width=5)
        for b in range(3):
            d.rectangle([x + b * 25, 940, x + b * 25 + 15, 962], fill=(200, 160, 110), outline=OUTL, width=4)
    river(d, T)
    for k in range(5):
        if (T * 3 + k) % 2 < 1.2:
            diamond(d, 120 + k * 200, 1240 + 10 * (k % 2), 18, glow=1)
    if lt > 0.5:
        top_label(frame, "UNTIL 1725", 380, YEL, 90)

def surat_props(frame, d, T, sc):
    lt = T - sc["s"]
    # polishing wheel on a bench, with a gem on the arm
    d.rectangle([380, 1260, 1000, 1330], fill=(140, 100, 70), outline=OUTL, width=6)
    cx, cy = 760, 1215
    d.ellipse([cx - 210, cy - 40, cx + 210, cy + 40], fill=(200, 200, 210), outline=OUTL, width=6)
    a = T * 12
    for k in range(6):
        x = cx + math.cos(a + k) * 180
        d.line([(x, cy - 25), (x, cy + 25)], fill=(140, 140, 150), width=4)
    d.line([(cx + 60, cy - 30), (cx + 160, cy - 140)], fill=OUTL, width=10)
    diamond(d, cx + 40, cy - 70, 46, glow=0.4 + 0.4 * abs(math.sin(T * 5)))
    if lt > 0.5:
        n = int(90 * clamp((lt - 0.5) / 2.0))
        top_label(frame, f"{n}% CUT IN SURAT", 380, YEL, 80)

def press_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a big hydraulic press squeezing a block
    d.rectangle([520, 860, 1020, 920], fill=(120, 130, 150), outline=OUTL, width=8)
    for x in (540, 960):
        d.rectangle([x, 920, x + 40, 1320], fill=(150, 160, 180), outline=OUTL, width=6)
    d.rectangle([500, 1320, 1040, 1380], fill=(120, 130, 150), outline=OUTL, width=8)
    p = ease_out(clamp((lt - 1.0) / 1.5))
    top = 940 + 210 * p
    d.rectangle([640, 920, 900, top], fill=(180, 190, 210), outline=OUTL, width=6)
    if lt < 3.0:
        d.rectangle([700, 1160, 840, 1320], fill=GRAY, outline=OUTL, width=6)
    else:
        diamond(d, 770, 1260, 60, glow=clamp((lt - 3.0) / 0.5))
    if lt > 0.5:
        top_label(frame, "1954 · LAB DIAMOND", 380, YEL, 76)

def fire_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 300, 1170
    # gas flame from a burner, diamond shrinking into CO2 puffs
    d.rectangle([cx - 60, 1300, cx + 60, 1380], fill=(90, 90, 100), outline=OUTL, width=6)
    fl = 1 + 0.08 * math.sin(T * 25)
    d.polygon([(cx - 70, 1300), (cx, 1300 - 230 * fl), (cx + 70, 1300)], fill=(255, 140, 40))
    d.polygon([(cx - 36, 1300), (cx, 1300 - 140 * fl), (cx + 36, 1300)], fill=(255, 230, 100))
    s = 1 - clamp((lt - 1.5) / 3.0)
    diamond(d, cx, 1000, 85 * s, glow=0.5, col=(255, 200, 150) if lt > 1.2 else ICE)
    if lt > 2.0:
        for k in range(4):
            ph = (lt * 0.6 + k * 0.25) % 1.0
            y = 940 - ph * 110; x = cx + (k - 1.5) * 110
            l = label("CO2", 44, WHITE); comp(frame, l, x - l.width / 2, y)
    if lt > 0.5:
        top_label(frame, "DIAMONDS BURN!", 380, YEL, 86)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="lead", s=4.0, e=11.0, bg="office", clock="STEP 1 · A PENCIL", char="kid", pos=(320, 1130, 420),
         props=lead_props, look=(0.6, 0),
         narr="Pencil 'lead' isn't lead at all. It's GRAPHITE mixed with CLAY.", n_at=4.2, narr_y=1560,
         say="So... no LEAD in it?", say_at=7.4, pitch=480),
    dict(id="atoms", s=11.0, e=18.0, bg="space", clock="SAME ATOMS",
         props=atoms_props,
         narr="Graphite is CARBON. Diamond is carbon too, just locked in a super-strong grid.", n_at=11.2,
         narr_y=1560),
    dict(id="squeeze", s=18.0, e=25.0, bg="gully", clock="STEP 2 · SQUEEZE", char="uncle", pos=(340, 1080, 440),
         props=squeeze_props, props_after=squeeze_after, look=(0.5, 0.2), state="angry",
         narr="You'd need about 50,000 TIMES air pressure, and over 1,000 °C.", n_at=18.2, narr_y=1560,
         say="Squeezing... HARDER!", say_at=21.4, pitch=150),
    dict(id="earth", s=25.0, e=32.0, bg="hot", clock="NATURE'S FACTORY", props=earth_props,
         narr="Nature does it about 200 KM underground. Then VOLCANOES blast diamonds up.", n_at=25.2,
         narr_y=1560),
    dict(id="golconda", s=32.0, e=39.0, bg="digsite", clock="INDIA · GOLCONDA", char="uncle", state="crown",
         pos=(270, 1100, 400), props=golconda_props, look=(0.5, 0.2),
         narr="Until 1725, every diamond on Earth came from INDIA, from rivers near GOLCONDA.", n_at=32.2,
         narr_y=1560, say="ALL of them? MINE!", say_at=35.4, pitch=150),
    dict(id="surat", s=39.0, e=46.0, bg="office", clock="TODAY · SURAT", char="uncle", state="hat",
         pos=(290, 1100, 420), props=surat_props, look=(0.6, 0.3),
         narr="Today about 90% of the world's diamonds are CUT and POLISHED in Surat.", n_at=39.2, narr_y=1560,
         say="Nine out of TEN!", say_at=42.4, pitch=150),
    dict(id="press", s=46.0, e=TW, bg="office", clock="1954 · THE LAB", char="kid", pos=(280, 1140, 380),
         props=press_props, look=(0.6, 0),
         narr="In 1954, a lab first made diamond using about 100,000 ATMOSPHERES of pressure.", n_at=46.2,
         narr_y=1560, say="Pencil to BLING!", say_at=49.6, pitch=480),
    dict(id="twist", s=TW, e=60.0, bg="living", clock="PLOT TWIST", char="uncle", state="angry",
         pos=(760, 1100, 420), props=fire_props, twist=True, look=(-0.6, 0.1),
         narr="Twist: diamonds can BURN! In very hot air they turn into CARBON DIOXIDE gas.", n_at=TW + 0.2,
         narr_y=1560, say="My diamond went POOF!", say_at=TW + 3.4, pitch=150),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        pencil(d, 180, 1420, 180 + 300 * p, 1420 - 80 * p, 46)
    if T >= 2.5:
        p = min(ease_back((T - 2.5) / 0.4), 1.2)
        diamond(d, 800, 1360, 110 * p, glow=1.0)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU SQUEEZED", WHITE)], 116), 730, 0.75, "right"),
        (title([("A PENCIL INTO", WHITE)], 116), 860, 1.0, "left"),
        (title([("A DIAMOND?", YEL)], 140), 990, 1.25, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Pencil or ", WHITE), ("DIAMOND", YEL)], 96), 470, 0.15),
                      (title([("in YOUR pocket?", WHITE)], 90), 600, 0.45)],
               row=[("kid", 1), ("uncle", "crown"), ("uncle", "hat"), ("kid", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0), dict(t0=18.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, minor=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    fx=[("pop", 1.95, 0.4), ("ding", 2.55, 0.3), ("pop", 4.4, 0.3), ("pop", 12.7, 0.3), ("rumble", 18.5, 0.25),
        ("click", 19.0, 0.2), ("click", 20.0, 0.2), ("click", 21.0, 0.2), ("rumble", 27.8, 0.4),
        ("boom", 28.2, 0.35), ("ding", 30.0, 0.3), ("ding", 35.0, 0.25), ("ding", 41.5, 0.25),
        ("crash", 47.3, 0.25), ("ding", 49.1, 0.35), ("whoosh", TW + 1.5, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_squeezed_a_pencil_into_a_diamond")
