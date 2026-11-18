#!/usr/bin/env python3
"""What if Africa split in two? Facts: the East African Rift runs for thousands of km from the Afar Triple Junction
in Ethiopia to Mozambique; the African plate is splitting into the Nubian and Somali plates at about 6-7 mm a year
(Wikipedia 'East African Rift', citing GPS studies). Fingernails grow ~3.47 mm a month, ~4 cm a year (Yaemsiri et
al. 2010, J Eur Acad Dermatol Venereol, via Harvard BioNumbers), so the rift is about 6x slower. In September 2005
a 60 km section of the rift in Afar, Ethiopia, opened up to 8 m in about three weeks as magma was injected (ESA
Envisat; Wright et al., Nature 2006). The viral March 2018 crack near Mai Mahiu, Kenya, was ash-filled fault ground
washed out by heavy rain (geologist David Adede via National Geographic). Ol Doinyo Lengai, Tanzania, is the only
active natrocarbonatite volcano; its lava erupts at ~500 °C, looks black and turns white within a day or two as it
reacts with moisture (Watchers / USGS-era measurements 1988; Wikipedia). Rupture and a new ocean basin are expected
in millions of years (estimates ~5-10 million years; NatGeo quotes tens of millions), cutting off the Somali plate.
Twist: India broke away near Madagascar in the late Cretaceous (~90-100 million years ago) and drifted north at up
to ~20 cm a year, vs ~2-4 cm for Africa today (Kumar et al. Nature 2007 via Discover; Wikipedia 'Indian plate')."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
SEA = (70, 140, 215)
SEA_D = (50, 110, 190)
LAND = (226, 186, 110)
LAND_E = (236, 150, 90)
GREEN = (140, 190, 100)
RED = (230, 60, 50)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2)):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, 0, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- geography (lon, lat)
AFRICA = [(-5.8, 35.8), (10.2, 37.2), (11, 36.8), (10, 33.9), (13.2, 32.9), (18.5, 30.3), (20, 32.1), (24, 32),
          (29.9, 31.2), (32.3, 31.3), (32.5, 29.9), (34.5, 26), (35.5, 24), (37.2, 19.6), (39.5, 15.6),
          (42.7, 13), (43.2, 11.6), (45, 10.4), (51.3, 11.8), (51.4, 10.4), (50, 8), (45.3, 2), (42.5, -0.4),
          (39.7, -4.1), (39.3, -6.8), (40.5, -10.7), (40.7, -15), (36.9, -17.9), (34.8, -19.8), (35.5, -23.9),
          (32.6, -25.9), (31, -29.9), (27.9, -33), (25.6, -34), (20, -34.8), (18.4, -34), (17.9, -31.5),
          (16.5, -28.6), (15.1, -26.6), (14.5, -22.9), (11.8, -17.3), (13.4, -12.6), (13.2, -8.8), (12.2, -6),
          (11.8, -4.8), (8.7, -0.7), (9.7, 4), (6, 4.3), (3.4, 6.4), (-0.2, 5.6), (-7.5, 4.4), (-10.8, 6.3),
          (-13.2, 8.5), (-13.7, 9.5), (-15.6, 11.9), (-17.5, 14.7), (-16, 18.1), (-17, 20.8), (-16, 23.7),
          (-12.9, 27.9), (-9.6, 30.4), (-7.6, 33.6), (-6.8, 34)]
MADAGASCAR = [(49.3, -12), (50.5, -15.5), (49.6, -17), (48, -21), (47.1, -25), (45.2, -25.5), (43.7, -23),
              (43.3, -21.5), (44.4, -16.2), (46.3, -15.7), (48, -13.5)]
ARABIA = [(32.6, 31.5), (34.2, 31.3), (34.9, 29.5), (36.5, 26), (39.2, 21.5), (42.5, 16.5), (43.4, 12.7),
          (45, 12.8), (52, 15.5), (59.8, 22.5), (58.6, 23.6), (56.3, 26.3), (51.5, 25.3), (48, 29.5),
          (48, 34), (36, 34)]
INDIA = [(68, 24), (71, 30), (74, 35), (78, 35.5), (80, 30), (88, 27), (92, 27.5), (97, 28), (94, 24), (92, 22),
         (89, 21.8), (86.9, 21), (85, 19.5), (82.3, 16.6), (80.3, 15.5), (80.2, 13), (79.8, 10.3), (77.5, 8.1),
         (76.3, 9.9), (74.8, 12.9), (73.8, 15.5), (72.8, 19), (72.6, 21.5), (70, 20.8), (69, 22.4), (68.4, 23.6)]
# main (eastern) branch of the rift, north to south
RIFT = [(41.8, 12.5), (40.5, 10), (39, 8), (38, 5.5), (36.2, 3.5), (36.2, 0), (35.9, -3.5), (35, -6.5),
        (34.2, -9.5), (34.6, -12.5), (35, -16), (35, -19.8)]
WEST_BRANCH = [(31, 2.5), (29.6, -1.5), (29.5, -6), (31, -8.5), (34.2, -9.5)]

class Proj:
    def __init__(self, lon0, lat0, cx, cy, k):
        self.lon0, self.lat0, self.cx, self.cy, self.k = lon0, lat0, cx, cy, k
    def __call__(self, pts, dx=0.0, dy=0.0):
        return [(self.cx + (lo - self.lon0) * self.k + dx, self.cy - (la - self.lat0) * self.k + dy) for lo, la in pts]

PA = Proj(17, 1, 540, 960, 12.0)   # Africa map: x 168..960, y 528..1386

def poly(d, pts, fill, w=5):
    d.polygon(pts, fill=fill, outline=OUTL, width=w)

_cache = {}
def sea_bg(T):
    if "sea" not in _cache:
        img = Image.new("RGBA", (W, H), SEA + (255,))
        d = ImageDraw.Draw(img)
        for k in range(26):
            y = 120 + k * 72
            for x in range((k % 2) * 60, W, 160):
                d.arc([x, y, x + 50, y + 22], 200, 340, fill=SEA_D, width=4)
        _cache["sea"] = img
    return _cache["sea"]

def ground_bg(key, sky_top, sky_bot, ground):
    if key not in _cache:
        y = np.linspace(0, 1, H)[:, None]
        a = (np.array(sky_top) * (1 - y[..., None]) + np.array(sky_bot) * y[..., None]).astype(np.uint8)
        img = Image.fromarray(np.broadcast_to(a, (H, W, 3)).copy()).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1180, W, H], fill=ground)
        _cache[key] = img
    return _cache[key]

def desert_bg(T): return ground_bg("desert", (120, 180, 240), (250, 226, 190), (214, 170, 110))
def kenya_bg(T): return ground_bg("kenya", (110, 130, 160), (190, 200, 210), (150, 110, 80))
def volcano_bg(T): return ground_bg("volc", (130, 190, 240), (230, 240, 250), (160, 150, 130))
def nails_bg(T): return ground_bg("nails", (255, 214, 170), (250, 190, 150), (220, 150, 110))

def africa_map(d, frame, split=0.0, glow=None, shift_e=(0, 0), east_col=None, madagascar=True, arabia=True):
    """Draw Africa; the Somali (east) piece is drawn separately so it can drift."""
    if arabia: poly(d, PA(ARABIA), LAND)
    land = Image.new("L", (W, H), 0)
    ImageDraw.Draw(land).polygon(PA(AFRICA), fill=255)
    east = Image.new("L", (W, H), 0)
    rp = PA(RIFT)
    ImageDraw.Draw(east).polygon(rp + [(rp[-1][0], 1500), (1100, 1500), (1100, 300), (rp[0][0] + 60, 300)], fill=255)
    e_mask = Image.fromarray((np.array(land) // 255 * np.array(east)).astype(np.uint8))
    w_mask = Image.fromarray((np.array(land) * (1 - np.array(east) // 255)).astype(np.uint8))
    lw = Image.new("RGBA", (W, H), LAND + (255,))
    frame.paste(lw, (0, 0), w_mask)
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).polygon(PA(AFRICA), outline=OUTL, width=5)
    if split <= 0:
        frame.paste(Image.new("RGBA", (W, H), (east_col or LAND) + (255,)), (0, 0), e_mask)
        frame.alpha_composite(edge)
    else:
        frame.alpha_composite(Image.composite(edge, Image.new("RGBA", (W, H), (0, 0, 0, 0)), w_mask.point(lambda v: 255 if v else 0)))
        # rift edge outline on the west piece
        d.line(rp, fill=OUTL, width=5, joint="curve")
        ex, ey = shift_e
        el = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        el.paste(Image.new("RGBA", (W, H), (east_col or LAND_E) + (255,)), (0, 0), e_mask)
        ImageDraw.Draw(el).line(rp, fill=OUTL, width=5, joint="curve")
        eo = Image.composite(edge, Image.new("RGBA", (W, H), (0, 0, 0, 0)), e_mask.point(lambda v: 255 if v else 0))
        el.alpha_composite(eo)
        frame.alpha_composite(el, (int(ex), int(ey)))
    if madagascar:
        poly(d, PA(MADAGASCAR, shift_e[0], shift_e[1]), LAND_E if split > 0 else LAND)
    if glow is not None:
        n = max(2, int(len(rp) * glow))
        pts = rp[:n]
        d.line(pts, fill=(255, 230, 120), width=22, joint="curve")
        d.line(pts, fill=RED, width=12, joint="curve")
        if glow >= 1:
            wp = PA(WEST_BRANCH)
            d.line(wp, fill=(255, 230, 120), width=16, joint="curve")
            d.line(wp, fill=RED, width=8, joint="curve")

def h_arrow(d, x, y, dirn, length=150, col=YEL):
    x1 = x + dirn * length
    d.rectangle([min(x, x1 - dirn * 40), y - 14, max(x, x1 - dirn * 40), y + 14], fill=col, outline=OUTL, width=4)
    d.polygon([(x1 - dirn * 50, y - 40), (x1, y), (x1 - dirn * 50, y + 40)], fill=col, outline=OUTL)

def v_arrow(d, x, y0, y1, col=YEL):
    d.rectangle([x - 14, y1 + 50, x + 14, y0], fill=col, outline=OUTL, width=4)
    d.polygon([(x - 40, y1 + 50), (x, y1), (x + 40, y1 + 50)], fill=col, outline=OUTL)

# ---------------------------------------------------------------- props
def crack_props(frame, d, T, sc):
    lt = T - sc["s"]
    africa_map(d, frame, glow=clamp((lt - 0.6) / 2.0))
    if lt > 2.0:
        lab_at(frame, "ETHIOPIA", 770, 760, WHITE, 40)
        lab_at(frame, "MOZAMBIQUE", 830, 1250, WHITE, 40)
    if lt > 0.4: top_label(frame, "EAST AFRICAN RIFT", 380, YEL, 80)

def plates_props(frame, d, T, sc):
    lt = T - sc["s"]
    gap = 6 * ease_out(clamp((lt - 1.0) / 3.0)) * (1 + 0.1 * math.sin(T * 3))
    africa_map(d, frame, split=1, shift_e=(gap, 0), glow=None)
    lab_at(frame, "NUBIAN", 380, 1000, WHITE, 52)
    lab_at(frame, "SOMALI", 900, 1100, WHITE, 46)
    if lt > 1.2:
        h_arrow(d, 330, 1080, -1, 140)
        h_arrow(d, 860, 1180, 1, 140)
    if lt > 2.4: top_label(frame, "~7 MM A YEAR", 380, YEL, 96)

def nail_draw(d, x, y, s, grow):
    # finger
    d.rounded_rectangle([x - 70 * s, y - 40 * s, x + 70 * s, y + 380 * s], radius=70 * s, fill=(232, 170, 130),
                        outline=OUTL, width=6)
    top = y - 40 * s - grow
    d.rounded_rectangle([x - 52 * s, top, x + 52 * s, y + 110 * s], radius=46 * s, fill=(255, 228, 228),
                        outline=OUTL, width=5)
    d.rectangle([x - 50 * s, top + 4, x + 50 * s, y - 20 * s], fill=(250, 250, 250))

def nails_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.8) / 3.5))
    nail_draw(d, 330, 820, 1.0, 120 * g)
    # rift ruler: two blocks parting
    gap = 20 * g
    d.rectangle([620, 900, 760 - gap / 2, 1120], fill=LAND, outline=OUTL, width=5)
    d.rectangle([760 + gap / 2, 900, 900, 1120], fill=LAND_E, outline=OUTL, width=5)
    lab_at(frame, "NAILS", 330, 560, WHITE, 58)
    lab_at(frame, "RIFT", 760, 840, WHITE, 58)
    if lt > 1.8:
        lab_at(frame, "~4 CM", 330, 1290, YEL, 64)
        lab_at(frame, "~0.7 CM", 760, 1190, YEL, 64)
    if lt > 0.4: top_label(frame, "IN ONE YEAR", 380, YEL, 96)

def afar_props(frame, d, T, sc):
    lt = T - sc["s"]
    op = ease_out(clamp((lt - 0.8) / 2.5))
    gap = 140 * op
    G = 1180
    # crack in the ground: a dark wedge with glowing magma at the bottom
    d.rectangle([0, G, W, H], fill=(214, 170, 110))
    d.polygon([(540 - gap, G), (540 + gap, G), (540 + gap * 0.25, G + 300), (540 - gap * 0.25, G + 300)],
              fill=(60, 40, 40))
    if op > 0.1:
        r = 30 + 10 * math.sin(T * 6)
        d.ellipse([540 - r, G + 270 - r * 0.6, 540 + r, G + 270 + r * 0.6], fill=(255, 120, 30))
    for k in range(5):
        x = 90 + k * 230
        if abs(x - 540) < gap + 40: continue
        d.polygon([(x - 30, G), (x + 30, G), (x, G - 50)], fill=(170, 130, 90), outline=OUTL)
    if lt > 1.6: lab_at(frame, "UP TO 8 M WIDE", 540, 1000, WHITE, 56)
    if lt > 0.4: top_label(frame, "AFAR, 2005", 380, YEL, 104)
    if lt > 2.6: lab_at(frame, "60 KM IN ~3 WEEKS", 540, 620, YEL, 64)

def kenya_props(frame, d, T, sc):
    lt = T - sc["s"]
    G = 1180
    d.rectangle([0, G - 60, W, G + 60], fill=(70, 70, 76))
    for x in range(0, W, 120):
        d.rectangle([x + 20, G - 6, x + 80, G + 6], fill=(240, 240, 240))
    d.polygon([(470, G - 60), (560, G - 60), (530, G + 60), (500, G + 60)], fill=(40, 30, 28))
    # rain
    rng = np.random.default_rng(7)
    for k in range(60):
        x0 = rng.uniform(0, W); y0 = rng.uniform(0, H)
        y = (y0 + T * 900) % 1100 + 450
        x = x0 - (y - 450) * 0.15
        d.line([(x, y), (x - 8, y + 34)], fill=(200, 220, 255), width=4)
    if lt > 1.5:
        q = ease_back(clamp((lt - 1.5) / 0.4))
        lab_at(frame, "SOFT ASH", 515, G + 160, WHITE, int(54 * q) + 2)
    if lt > 0.4: top_label(frame, "KENYA, 2018", 380, YEL, 104)
    if lt > 3.2: lab_at(frame, "RAIN WASHED IT OUT", 540, 620, YEL, 64)

def volcano_props(frame, d, T, sc):
    lt = T - sc["s"]
    G = 1180
    d.polygon([(120, G), (460, 660), (620, 660), (960, G)], fill=(150, 130, 110), outline=OUTL)
    wh = clamp((lt - 2.6) / 2.0)
    # lava flows: black, then white
    col = tuple(int(30 + (245 - 30) * wh) for _ in range(3))
    flow = ease_out(clamp((lt - 0.5) / 1.6))
    for side, x0 in ((-1, 490), (1, 590)):
        pts = []
        for k in range(12):
            t = k / 11 * flow
            pts.append((x0 + side * (t * 300 + 20 * math.sin(t * 9)), 670 + t * 480))
        if len(pts) > 1: d.line(pts, fill=col, width=46, joint="curve")
    if lt < 2.6:
        for k in range(4):
            r = 16 + 6 * math.sin(T * 5 + k)
            d.ellipse([530 + k * 10 - r, 620 - k * 40 - r, 530 + k * 10 + r, 620 - k * 40 + r], fill=(40, 40, 40))
    lab_at(frame, "~500 °C", 830, 760, YEL, 66)
    lab_at(frame, "BLACK" if wh < 0.5 else "WHITE!", 260, 820, WHITE, 66)
    if lt > 0.4: top_label(frame, "OL DOINYO LENGAI", 380, YEL, 84)

def ocean_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.6) / 4.2))
    africa_map(d, frame, split=1, shift_e=(70 * p, 26 * p))
    lab_at(frame, "NEW OCEAN", 780 + 30 * p, 1340, WHITE, 52)
    lab_at(frame, "SOMALIA", 890 + 70 * p, 860 + 26 * p, WHITE, 40)
    if lt > 0.4: top_label(frame, "MILLIONS OF YEARS", 380, YEL, 84)

PI = Proj(64, 3, 540, 960, 9.0)   # twist map: x ~ 18..1080
def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # Asia band on top
    d.rectangle([0, 450, W, PI([(0, 31)])[0][1]], fill=GREEN, outline=OUTL, width=5)
    lab_at(frame, "ASIA", 820, 520, WHITE, 50)
    poly(d, PI(AFRICA), LAND)
    poly(d, PI(ARABIA), LAND)
    poly(d, PI(MADAGASCAR), LAND)
    p = ease_out(clamp((lt - 0.8) / 3.6))
    # India starts snug against Madagascar and moves north-east to today
    start = (-21 * 9.0, 28 * 9.0)
    dx, dy = start[0] * (1 - p), start[1] * (1 - p)
    poly(d, PI(INDIA, dx, dy), (250, 160, 70))
    cx, cy = PI([(79, 20)], dx, dy)[0]
    lab_at(frame, "INDIA", cx, cy, WHITE, 52)
    if p > 0.95:
        for k in range(5):
            x0, y0 = PI([(74 + k * 4.5, 32)])[0]
            d.polygon([(x0 - 26, y0 + 10), (x0, y0 - 40), (x0 + 26, y0 + 10)], fill=(250, 252, 255), outline=OUTL)
    if lt > 0.3: top_label(frame, "UP TO ~20 CM A YEAR", 345, YEL, 72)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="crack", s=4.0, e=11.0, bg_fn=sea_bg, clock="RIGHT NOW", props=crack_props,
         narr="Africa is already CRACKING. The East African Rift runs THOUSANDS of km.", n_at=4.2,
         narr_y=1580),
    dict(id="plates", s=11.0, e=18.0, bg_fn=sea_bg, clock="TWO PLATES", props=plates_props,
         narr="Two pieces, the NUBIAN and SOMALI plates, pull apart about 7 MM a year.", n_at=11.2,
         narr_y=1580),
    dict(id="nails", s=18.0, e=25.0, bg_fn=nails_bg, clock="SO SLOW", props=nails_props,
         narr="That's about 6 TIMES slower than your fingernails grow.", n_at=18.2, narr_y=1580),
    dict(id="afar", s=25.0, e=32.0, bg_fn=desert_bg, clock="ETHIOPIA", props=afar_props, char="kid",
         pos=(170, 1110, 200), look=(0.6, 0.4),
         narr="But it can JUMP. In 2005, magma tore open a 60 KM crack in Ethiopia in about 3 weeks.",
         n_at=25.2, narr_y=1580),
    dict(id="kenya", s=32.0, e=39.0, bg_fn=kenya_bg, clock="MYTH CHECK", props=kenya_props,
         narr="That viral 2018 crack in KENYA? Mostly RAIN washing soft ash out of old ground.",
         n_at=32.2, narr_y=1580),
    dict(id="volcano", s=39.0, e=46.0, bg_fn=volcano_bg, clock="TANZANIA", props=volcano_props,
         narr="The rift even built a weird volcano. Its lava comes out BLACK at ~500 °C, then turns WHITE.",
         n_at=39.2, narr_y=1580),
    dict(id="ocean", s=46.0, e=TW, bg_fn=sea_bg, clock="THE FUTURE", props=ocean_props,
         narr="In MILLIONS of years, the sea could flood in, carving out a NEW OCEAN.", n_at=46.2,
         narr_y=1580),
    dict(id="twist", s=TW, e=60.0, bg_fn=sea_bg, clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: INDIA did this first! It broke away near Madagascar and RACED north.", n_at=TW + 0.2,
         narr_y=1580),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.1)
        k = 4.6 * p + 0.01
        pts = [(540 + (lo - 17) * k, 1500 - (la - 1) * k) for lo, la in AFRICA]
        d.polygon(pts, fill=LAND, outline=OUTL, width=5)
        rp = [(540 + (lo - 17) * k, 1500 - (la - 1) * k) for lo, la in RIFT]
        if p > 0.9: d.line(rp, fill=RED, width=8, joint="curve")

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("AFRICA SPLIT", WHITE)], 140), 690, 0.75, "right"),
        (title([("IN TWO?", YEL)], 160), 840, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which side would ", WHITE)], 96), 470, 0.15),
                      (title([("YOU", YEL), (" pick?", WHITE)], 104), 600, 0.45)],
               row=[("kid", 1), ("earth", 1), ("uncle", "hat"), ("fish", 1), ("chai", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=39.0, minor=True), dict(t0=39.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, minor=True, drums=False), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=46.0, dur=7.0, g=0.10), dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("rumble", 4.8, 0.2, dict(dd=2.0)), ("rumble", 12.0, 0.15, dict(dd=3.0)), ("ding", 20.5, 0.2),
        ("crash", 26.0, 0.25), ("rumble", 26.2, 0.25, dict(dd=2.5)), ("wind", 32.3, 0.2, dict(dd=6.0)),
        ("bubbles", 39.6, 0.15, dict(dd=3.0)), ("ding", 42.0, 0.2), ("waves", 46.5, 0.25, dict(dd=6.0)),
        ("rumble", TW + 1.0, 0.2, dict(dd=3.0)), ("ding", TW + 4.6, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_africa_split_in_two")
