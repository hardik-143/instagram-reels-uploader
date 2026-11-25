#!/usr/bin/env python3
"""What if you visited India's only active volcano? Facts: Barren Island, Andaman Sea, about 138 km NE of Port
Blair (Wikipedia; Smithsonian GVP: ~135 km). 'The only confirmed active volcano in the Indian subcontinent'
(Wikipedia); 'the only active volcano in India as well as in the entire South Asian region' (Free Press Journal,
25 Sep 2025); 'India's only active volcano' (Down To Earth). Island ~353-354 m high, ~3 km wide (Wikipedia; GVP);
it 'rises from a depth of about 2,250 m' (GVP). Caldera 'roughly 2-km-wide... with walls 250-350 m high' (GVP).
First recorded eruption 1787 (Wikipedia, DTE); quiet for over a century (DTE: 159 years) until 1991; lava flows
reached the sea in 1991 and 1995 (GVP); 1991 eruption destroyed the lighthouse (Wikipedia, Roundglass). Erupted on
13 and 20 September 2025, the second two days after a magnitude 4.2 quake on 18 Sep (DTE; Free Press Journal).
Uninhabited; landing prohibited, visitors view by boat; divers explore coral on dark ash-like black sand (Free
Press; Roundglass; Wikipedia). Twist: goats 'brought here by British sailors from a steamer leaving Port Blair in
1891', 'surviving on two fresh water springs and thick vegetation' (Wikipedia; GVP; Roundglass)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 53.0
SEA = (60, 130, 205)
SEA_D = (42, 100, 180)
DEEP = (24, 50, 110)
ROCK = (110, 96, 88)
ROCK_D = (80, 68, 62)
GREEN = (96, 160, 90)
LAVA = (255, 110, 30)
LAVA_Y = (255, 210, 80)
SMOKE = (120, 120, 126)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col); comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2)):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, 0, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def sea_bg(T):
    if "sea" not in _bgc:
        img = Image.new("RGBA", (W, H), SEA + (255,)); d = ImageDraw.Draw(img)
        for k in range(26):
            y = 120 + k * 72
            for x in range((k % 2) * 60, W, 160):
                d.arc([x, y, x + 50, y + 22], 200, 340, fill=SEA_D, width=4)
        _bgc["sea"] = img
    return _bgc["sea"]

def sky_bg(key, stops):
    if key not in _bgc:
        img = grad(stops, W, H); d = ImageDraw.Draw(img)
        d.rectangle([0, 1180, W, H], fill=SEA)
        for k in range(8):
            y = 1200 + k * 60
            for x in range((k % 2) * 70, W, 180):
                d.arc([x, y, x + 60, y + 24], 200, 340, fill=SEA_D, width=4)
        _bgc[key] = img
    return _bgc[key]

def day_bg(T): return sky_bg("day", [(0, (120, 180, 240)), (1, (226, 238, 250))])
def dusk_bg(T): return sky_bg("dusk", [(0, (70, 60, 130)), (0.6, (240, 140, 110)), (1, (255, 200, 150))])

def cut_bg(T):
    if "cut" not in _bgc:
        img = grad([(0, (130, 190, 240)), (1, (220, 236, 250))], W, H); d = ImageDraw.Draw(img)
        y0 = 760
        for k in range(H - y0):
            t = k / (H - y0)
            c = tuple(int(SEA[i] * (1 - t) + DEEP[i] * t) for i in range(3))
            d.line([(0, y0 + k), (W, y0 + k)], fill=c)
        _bgc["cut"] = img
    return _bgc["cut"]

# ---------------------------------------------------------------- drawing helpers
def puff(d, x, y, r, col=SMOKE):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=OUTL, width=4)

def smoke(d, x, y, T, n=5, big=1.0):
    for k in range(n):
        ph = (T * 0.5 + k / n) % 1.0
        r = (26 + 50 * ph) * big
        puff(d, x + 40 * math.sin(ph * 4 + k) + 60 * ph, y - 320 * ph * big, r,
             tuple(int(c + 60 * ph) for c in SMOKE))

def volcano(d, cx, base_y, w, h, T, lava=0.0, crater=True):
    top = base_y - h
    tw = w * 0.16
    d.polygon([(cx - w / 2, base_y), (cx - tw, top), (cx + tw, top), (cx + w / 2, base_y)], fill=ROCK, outline=OUTL)
    # green lower slopes
    d.polygon([(cx - w / 2, base_y), (cx - w * 0.36, base_y - h * 0.32), (cx - w * 0.2, base_y - h * 0.22),
               (cx - w * 0.1, base_y)], fill=GREEN)
    d.polygon([(cx + w * 0.12, base_y), (cx + w * 0.3, base_y - h * 0.3), (cx + w * 0.42, base_y - h * 0.2),
               (cx + w / 2, base_y)], fill=GREEN)
    d.line([(cx - w / 2, base_y), (cx - tw, top), (cx + tw, top), (cx + w / 2, base_y)], fill=OUTL, width=5)
    if crater:
        d.ellipse([cx - tw, top - 12, cx + tw, top + 12], fill=ROCK_D, outline=OUTL, width=4)
    if lava > 0:
        pts = []
        for k in range(14):
            t = k / 13 * lava
            pts.append((cx + 0.55 * t * w / 2 + 14 * math.sin(t * 10), top + t * h))
        if len(pts) > 1:
            d.line(pts, fill=LAVA, width=30, joint="curve")
            d.line(pts, fill=LAVA_Y, width=10, joint="curve")

def boat(d, x, y, s=1.0, T=0.0):
    bob = 6 * math.sin(T * 2.4)
    y = y + bob
    d.polygon([(x - 170 * s, y), (x + 170 * s, y), (x + 120 * s, y + 70 * s), (x - 120 * s, y + 70 * s)],
              fill=(240, 240, 240), outline=OUTL)
    d.rectangle([x - 150 * s, y - 8 * s, x + 150 * s, y + 10 * s], fill=(220, 70, 60), outline=OUTL, width=4)
    d.rectangle([x - 40 * s, y - 90 * s, x + 70 * s, y - 8 * s], fill=(250, 220, 120), outline=OUTL, width=4)
    return y

def goat(d, x, y, s=1.0, T=0.0, flip=1, chew=0.0):
    """Simple side-view cartoon goat standing on y (hooves), facing right if flip=1."""
    def P(px, py): return (x + flip * px * s, y + py * s)
    body = [P(-70, -150), P(60, -150), P(70, -90), P(-70, -90)]
    for lx in (-55, -30, 30, 55):
        d.rectangle([min(P(lx - 8, 0)[0], P(lx + 8, 0)[0]), y - 100 * s, max(P(lx - 8, 0)[0], P(lx + 8, 0)[0]), y],
                    fill=(235, 225, 210), outline=OUTL, width=3)
    d.rounded_rectangle([min(P(-80, 0)[0], P(80, 0)[0]), y - 165 * s, max(P(-80, 0)[0], P(80, 0)[0]), y - 85 * s],
                        radius=int(36 * s), fill=(245, 238, 225), outline=OUTL, width=4)
    # tail
    d.polygon([P(-78, -150), P(-100, -175), P(-84, -140)], fill=(245, 238, 225), outline=OUTL)
    # neck + head
    d.polygon([P(50, -150), P(80, -215), P(108, -205), P(80, -130)], fill=(245, 238, 225), outline=OUTL)
    hx, hy = P(110, -215)
    d.ellipse([hx - 38 * s, hy - 26 * s, hx + 38 * s, hy + 26 * s], fill=(245, 238, 225), outline=OUTL, width=4)
    # horns
    d.line([P(96, -236), P(80, -276), P(64, -282)], fill=(150, 120, 90), width=int(9 * s), joint="curve")
    # ear
    d.polygon([P(88, -222), P(58, -214), P(86, -206)], fill=(220, 200, 180), outline=OUTL)
    # beard, chewing
    by = 8 * s * math.sin(T * 10) * chew
    d.polygon([P(126, -196), P(118, -160 + by / s), P(136, -194)], fill=(220, 210, 195), outline=OUTL)
    # eye
    ex, ey = P(116, -222)
    d.ellipse([ex - 6 * s, ey - 6 * s, ex + 6 * s, ey + 6 * s], fill=OUTL)

# ---------------------------------------------------------------- Andaman map (lon, lat)
PM = lambda lo, la: (540 + (lo - 93.0) * 300, 1040 - (la - 12.0) * 300)
ISLANDS = [  # stylised Andaman chain: (lon, lat, rx_deg, ry_deg)
    (92.95, 13.2, 0.17, 0.45), (92.9, 12.45, 0.16, 0.4), (92.7, 11.75, 0.17, 0.38),
    (93.0, 11.98, 0.05, 0.06), (92.55, 10.65, 0.14, 0.14)]
def map_props(frame, d, T, sc):
    lt = T - sc["s"]
    for lo, la, rx, ry in ISLANDS:
        x, y = PM(lo, la)
        d.ellipse([x - rx * 300, y - ry * 300, x + rx * 300, y + ry * 300], fill=(150, 200, 110), outline=OUTL,
                  width=5)
    pbx, pby = PM(92.73, 11.62)
    d.ellipse([pbx - 16, pby - 16, pbx + 16, pby + 16], fill=WHITE, outline=OUTL, width=4)
    lab_at(frame, "PORT BLAIR", pbx - 40, pby + 60, WHITE, 44)
    bx, by = PM(93.86, 12.28)
    p = ease_back(clamp((lt - 0.8) / 0.6))
    if p > 0:
        r = 30 * p
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=ROCK, outline=OUTL, width=5)
        d.ellipse([bx - r * 0.45, by - r * 0.45, bx + r * 0.45, by + r * 0.45], fill=LAVA)
    if lt > 1.4:
        smoke(d, bx, by - 30, T, 4, 0.5)
        lab_at(frame, "BARREN", 880, by + 80, YEL, 54)
        lab_at(frame, "ISLAND", 880, by + 134, YEL, 54)
    if lt > 2.4:
        q = ease_out(clamp((lt - 2.4) / 1.2))
        x1 = pbx + (bx - pbx) * q; y1 = pby + (by - pby) * q
        for k in range(12):
            t0, t1 = k / 12, (k + 0.5) / 12
            if t0 > q: break
            d.line([(pbx + (bx - pbx) * t0, pby + (by - pby) * t0),
                    (pbx + (bx - pbx) * min(t1, q), pby + (by - pby) * min(t1, q))], fill=YEL, width=8)
        if q > 0.9: lab_at(frame, "~138 KM", 720, 1140, WHITE, 52)
    if lt > 0.3: top_label(frame, "ANDAMAN SEA", 380, YEL, 84)

def only_props(frame, d, T, sc):
    lt = T - sc["s"]
    volcano(d, 540, 1190, 820, 430, T)
    smoke(d, 560, 740, T, 6, 1.0)
    if lt > 1.2:
        q = ease_back(clamp((lt - 1.2) / 0.5))
        if lt < 3.6: lab_at(frame, "ACTIVE!", 540, 1300, YEL, int(90 * q) + 2)
    if lt > 3.6: lab_at(frame, "ONLY ONE IN SOUTH ASIA", 540, 1300, YEL, 60)
    if lt > 0.3: top_label(frame, "INDIA'S ONLY ONE", 380, YEL, 84)

def ice_props(frame, d, T, sc):
    lt = T - sc["s"]
    SL = 760
    sea_top = SL
    # full cone: 350 m above (scaled up for visibility) and 2,250 m below
    p = ease_out(clamp((lt - 1.4) / 2.0))
    k = 0.36  # px per metre below
    base = SL + 2250 * k * p + 4
    top = SL - 130
    d.polygon([(300, SL), (480, top), (600, top), (780, SL)], fill=ROCK, outline=OUTL)
    d.line([(300, SL), (480, top), (600, top), (780, SL)], fill=OUTL, width=5)
    if p > 0:
        bw = 300 + 400 * p
        d.polygon([(300, SL), (780, SL), (540 + bw, base), (540 - bw, base)], fill=ROCK_D, outline=OUTL)
    d.line([(0, SL), (W, SL)], fill=WHITE, width=6)
    lab_at(frame, "SEA LEVEL", 150, SL + 40, WHITE, 40)
    lab_at(frame, "~350 M", 890, SL - 70, YEL, 62)
    if p > 0.6:
        lab_at(frame, "~2,250 M", 540, SL + 2250 * k * 0.55, YEL, 74)
        lab_at(frame, "DEEP", 540, SL + 2250 * k * 0.55 + 74, WHITE, 56)
    if lt > 0.3: top_label(frame, "LIKE AN ICEBERG", 380, YEL, 84)

def crater_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1000
    p = ease_back(clamp((lt - 0.3) / 0.6))
    R = 380 * p
    if R > 4:
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=GREEN, outline=OUTL, width=6)
        r2 = R * 0.7
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=ROCK, outline=OUTL, width=5)
        # caldera open to the west (sea breach), cone in the middle
        d.polygon([(cx - r2 - 6, cy - 60 * p), (cx - R - 10, cy - 90 * p), (cx - R - 10, cy + 90 * p),
                   (cx - r2 - 6, cy + 60 * p)], fill=ROCK)
        r3 = R * 0.2
        d.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], fill=ROCK_D, outline=OUTL, width=5)
        d.ellipse([cx - r3 * 0.4, cy - r3 * 0.4, cx + r3 * 0.4, cy + r3 * 0.4], fill=LAVA)
    if lt > 1.2:
        smoke(d, cx, cy - 40, T, 4, 0.6)
    if lt > 1.8:
        d.line([(cx - 266, 1330), (cx + 266, 1330)], fill=YEL, width=8)
        for x in (cx - 266, cx + 266): d.line([(x, 1310), (x, 1350)], fill=YEL, width=8)
        lab_at(frame, "CRATER ~2 KM", cx, 1290 - 6, WHITE, 50)
    if lt > 0.3: top_label(frame, "ISLAND ~3 KM WIDE", 380, YEL, 80)

def history_props(frame, d, T, sc):
    lt = T - sc["s"]
    volcano(d, 540, 1190, 760, 400, T, lava=ease_out(clamp((lt - 3.4) / 2.2)))
    if lt > 3.4: smoke(d, 560, 770, T, 6, 1.0)
    # timeline chips
    if lt > 0.5:
        lab_at(frame, "1787", 190, 620, YEL, 80)
        lab_at(frame, "FIRST", 190, 700, WHITE, 44)
    if 1.8 < lt < 4.8:
        lab_at(frame, "100+ YEARS OF QUIET", 540, 1300, WHITE, 60)
    if lt > 3.2:
        q = ease_back(clamp((lt - 3.2) / 0.5))
        lab_at(frame, "1991", 890, 620, YEL, int(90 * q) + 2)
    if lt > 5.0: lab_at(frame, "LAVA HIT THE SEA", 540, 1300, YEL, 60)
    if lt > 0.2: top_label(frame, "ERUPTION DIARY", 380, YEL, 84)

def recent_props(frame, d, T, sc):
    lt = T - sc["s"]
    shake = 10 * math.sin(T * 60) * (1 if 0.8 < lt < 1.8 else 0)
    volcano(d, 540 + shake, 1190, 760, 400, T)
    for i, t0 in enumerate((2.2, 4.0)):
        if lt > t0:
            ph = clamp((lt - t0) / 1.4)
            puff(d, 560, 780 - 220 * ph, 40 + 60 * ph)
    if 0.8 < lt < 2.6: lab_at(frame, "4.2 QUAKE", 540, 1300, WHITE, 60)
    if lt > 2.4: lab_at(frame, "13 SEP", 220, 640, YEL, 64)
    if lt > 4.2: lab_at(frame, "20 SEP", 860, 640, YEL, 64)
    if lt > 0.2: top_label(frame, "SEPTEMBER 2025", 380, YEL, 84)

def visit_props(frame, d, T, sc):
    lt = T - sc["s"]
    volcano(d, 820, 1190, 600, 320, T)
    smoke(d, 840, 870, T, 5, 0.8)
    y = boat(d, 300, 1150, 1.0, T)
    mini(frame, "kid", 300, y - 160, 230, T, look=(0.7, -0.2))
    # no-landing sign on the shore
    if lt > 1.0:
        d.rectangle([594, 1060, 606, 1180], fill=(120, 90, 60))
        d.rounded_rectangle([520, 960, 680, 1070], radius=14, fill=(230, 60, 50), outline=OUTL, width=5)
        lab_at(frame, "NO", 600, 994, WHITE, 40)
        lab_at(frame, "LANDING", 600, 1036, WHITE, 32)
    if lt > 3.6:
        # diver bubbles + coral on black sand strip
        d.rectangle([0, 1350, W, 1430], fill=(40, 40, 46))
        for k, x in enumerate((140, 330, 520, 720, 900)):
            col = [(255, 120, 140), (255, 190, 80), (180, 120, 255), (90, 220, 200), (255, 150, 90)][k]
            d.ellipse([x - 40, 1300, x + 40, 1370], fill=col, outline=OUTL, width=4)
        lab_at(frame, "BLACK ASH SAND", 540, 1250, WHITE, 46)
    if lt > 0.2: top_label(frame, "LOOK, DON'T LAND", 380, YEL, 84)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    volcano(d, 540, 1190, 1000, 420, T, crater=True)
    smoke(d, 560, 760, T, 5, 0.9)
    n = 0
    for k, (x, y, s, fl, t0) in enumerate([(250, 1150, 0.9, 1, 0.8), (800, 1140, 0.8, -1, 1.4),
                                           (460, 1050, 0.6, 1, 2.0), (650, 1010, 0.5, -1, 2.3)]):
        if lt > t0:
            q = ease_back(clamp((lt - t0) / 0.4))
            goat(d, x, y, s * q, T + k, fl, chew=1.0)
    if lt > 3.4:
        lab_at(frame, "SINCE 1891", 540, 1300, YEL, 72)
    if lt > 0.2: top_label(frame, "THE ONLY LOCALS", 380, YEL, 84)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="map", s=4.0, e=11.0, bg_fn=sea_bg, clock="ANDAMANS", props=map_props,
         narr="Meet BARREN ISLAND, about 138 KM from Port Blair, in the Andaman Sea.", n_at=4.2, narr_y=1580),
    dict(id="only", s=11.0, e=18.0, bg_fn=day_bg, clock="ACTIVE", props=only_props,
         narr="It's India's ONLY confirmed active volcano, and the only one in SOUTH ASIA.", n_at=11.2,
         narr_y=1580),
    dict(id="ice", s=18.0, e=25.0, bg_fn=cut_bg, clock="HIDDEN", props=ice_props,
         narr="The island is only ~350 M tall. The rest hides UNDERWATER, rising from ~2,250 M deep.",
         n_at=18.2, narr_y=1580),
    dict(id="crater", s=25.0, e=32.0, bg_fn=sea_bg, clock="FROM ABOVE", props=crater_props,
         narr="Inside sits a crater about 2 KM wide, with walls up to 350 M high.", n_at=25.2, narr_y=1580),
    dict(id="history", s=32.0, e=39.0, bg_fn=day_bg, clock="1787-1991", props=history_props,
         narr="First recorded eruption: 1787. Then over a CENTURY of quiet, until 1991 sent LAVA into the sea.",
         n_at=32.2, narr_y=1580),
    dict(id="recent", s=39.0, e=46.0, bg_fn=dusk_bg, clock="LAST YEAR", props=recent_props,
         narr="In September 2025, right after a 4.2 quake, it erupted TWICE in 8 DAYS.", n_at=39.2,
         narr_y=1580),
    dict(id="visit", s=46.0, e=TW, bg_fn=day_bg, clock="VISITING", props=visit_props,
         narr="Landing is BANNED. You watch from a BOAT, while divers explore coral on black ash sand.",
         n_at=46.2, narr_y=1600),
    dict(id="twist", s=TW, e=60.0, bg_fn=day_bg, clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: no humans live there, but GOATS do! Left by a steamer in 1891, they drink from fresh springs.",
         n_at=TW + 0.2, narr_y=1590),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.1)
        volcano(d, 540, 1560, 560 * p + 1, 300 * p + 1, T)
        if p > 0.9: smoke(d, 550, 1270, T, 4, 0.6)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 470, 0.2, "pop"),
        (title([("YOU VISITED INDIA'S", WHITE)], 96), 680, 0.75, "right"),
        (title([("ONLY VOLCANO?", YEL)], 130), 800, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL)], 104), 470, 0.15),
                      (title([("go see it?", WHITE)], 104), 600, 0.45)],
               row=[("kid", 1), ("earth", 1), ("uncle", "hat"), ("fish", 1), ("chai", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0, minor=True), dict(t0=46.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=39.0, dur=7.0, g=0.10)],
    fx=[("waves", 4.3, 0.2, dict(dd=5.0)), ("rumble", 11.5, 0.2, dict(dd=3.0)), ("bubbles", 19.5, 0.15, dict(dd=4.0)),
        ("ding", 27.0, 0.2), ("rumble", 35.4, 0.25, dict(dd=3.0)), ("splash", 37.4, 0.25),
        ("rumble", 39.8, 0.3, dict(dd=1.5)), ("boom", 41.2, 0.25), ("boom", 43.0, 0.25),
        ("waves", 46.3, 0.2, dict(dd=6.0)), ("seagulls", 47.0, 0.15), ("ding", TW + 3.6, 0.2)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_visited_indias_only_volcano")
