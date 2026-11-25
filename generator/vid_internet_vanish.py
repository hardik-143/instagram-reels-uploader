#!/usr/bin/env python3
"""What if the internet vanished for a day? Facts: UPI processed an average of 822 million (~82 crore) transactions
a day in October 2026, a record 25.47 billion for the month, worth ~Rs 1 lakh crore a day (NPCI data via Inc42,
2 Nov 2026). GPS receivers only receive satellite signals (one-way broadcast), so a phone's GPS fix needs no
internet (GPS.gov). TeleGeography confirms submarine cables carry over 99% of intercontinental data traffic
(TeleGeography 'Mythbusting part 3', 2023). 'Over 1.5 million kilometers of submarine cables in service' as of early
2026, and 'more than 600 active and planned' cables (TeleGeography Submarine Cable FAQ); Earth's circumference
~40,075 km, so 1.5M km is ~37 laps. 'Typically as wide as a garden hose', fibres 'roughly the diameter of a human
hair' (TeleGeography FAQ). 'Roughly 200 faults each year' (ICPC via TeleGeography); fishing vessels and ships
dragging anchors cause two-thirds; shark bites 'exceedingly rare', fish bites caused zero faults 2007-2014
(TeleGeography FAQ). Twist: first ARPANET message, 29 Oct 1969, UCLA to SRI: they tried to type 'login', 'l' and
'o' got through, then the system crashed (Leonard Kleinrock, UCLA)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 53.0
SEA = (40, 90, 170)
SEA_D = (30, 72, 150)
LAND = (120, 190, 110)
RED = (230, 60, 50)
GREEN_OK = (70, 200, 110)
GREY = (70, 74, 86)
CABLE = (255, 200, 60)

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
def room_bg(T):
    if "room" not in _bgc:
        img = grad([(0, (255, 226, 180)), (1, (250, 200, 150))], W, H); d = ImageDraw.Draw(img)
        d.rectangle([0, 1300, W, H], fill=(190, 140, 100))
        d.rectangle([60, 560, 280, 760], fill=(150, 210, 250), outline=OUTL, width=6)
        d.line([(170, 560), (170, 760)], fill=OUTL, width=5); d.line([(60, 660), (280, 660)], fill=OUTL, width=5)
        _bgc["room"] = img
    return _bgc["room"]

def street_bg(T):
    if "street" not in _bgc:
        img = grad([(0, (130, 190, 240)), (1, (230, 240, 250))], W, H); d = ImageDraw.Draw(img)
        d.rectangle([0, 1300, W, H], fill=(150, 150, 156))
        for x in (40, 300, 820):
            d.rectangle([x, 760, x + 220, 1300], fill=(240, 200, 150), outline=OUTL, width=5)
            for wy in (820, 960, 1100):
                d.rectangle([x + 40, wy, x + 100, wy + 70], fill=(150, 210, 250), outline=OUTL, width=4)
        _bgc["street"] = img
    return _bgc["street"]

def sea_bg(T):
    if "sea" not in _bgc:
        img = Image.new("RGBA", (W, H), SEA + (255,)); d = ImageDraw.Draw(img)
        for k in range(26):
            y = 120 + k * 72
            for x in range((k % 2) * 60, W, 160):
                d.arc([x, y, x + 50, y + 22], 200, 340, fill=SEA_D, width=4)
        _bgc["sea"] = img
    return _bgc["sea"]

def space_bg(T):
    if "space" not in _bgc:
        img = grad([(0, (16, 20, 50)), (1, (40, 40, 90))], W, H); d = ImageDraw.Draw(img)
        rng = np.random.default_rng(3)
        for _ in range(120):
            x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3.5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
        _bgc["space"] = img
    return _bgc["space"]

def seabed_bg(T):
    if "bed" not in _bgc:
        img = grad([(0, (40, 120, 190)), (1, (14, 40, 90))], W, H); d = ImageDraw.Draw(img)
        d.rectangle([0, 1240, W, H], fill=(194, 170, 120))
        _bgc["bed"] = img
    return _bgc["bed"]

def lab_bg(T):
    if "lab" not in _bgc:
        img = grad([(0, (230, 220, 200)), (1, (200, 190, 170))], W, H); d = ImageDraw.Draw(img)
        d.rectangle([0, 1300, W, H], fill=(150, 120, 90))
        _bgc["lab"] = img
    return _bgc["lab"]

# ---------------------------------------------------------------- drawing helpers
def phone(d, cx, cy, s, screen_fn=None):
    w, h = 300 * s, 560 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(40 * s), fill=(40, 40, 50),
                        outline=OUTL, width=6)
    sx0, sy0, sx1, sy1 = cx - w / 2 + 18 * s, cy - h / 2 + 40 * s, cx + w / 2 - 18 * s, cy + h / 2 - 40 * s
    d.rectangle([sx0, sy0, sx1, sy1], fill=(245, 245, 250))
    if screen_fn: screen_fn(d, sx0, sy0, sx1, sy1)
    return sx0, sy0, sx1, sy1

def wifi_x(d, cx, cy, r, col=GREY):
    for k, rr in enumerate((r, r * 0.68, r * 0.36)):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 225, 315, fill=col, width=int(r * 0.12))
    d.ellipse([cx - r * 0.1, cy - r * 0.1, cx + r * 0.1, cy + r * 0.1], fill=col)
    o = r * 0.55
    d.line([(cx - o, cy - r * 1.05), (cx + o, cy - r * 0.05)], fill=RED, width=int(r * 0.16))
    d.line([(cx + o, cy - r * 1.05), (cx - o, cy - r * 0.05)], fill=RED, width=int(r * 0.16))

def qr(d, x0, y0, size, seed=5):
    n = 11
    c = size / n
    rng = np.random.default_rng(seed)
    d.rectangle([x0, y0, x0 + size, y0 + size], fill=WHITE, outline=OUTL, width=4)
    for i in range(n):
        for j in range(n):
            corner = (i < 3 and j < 3) or (i < 3 and j > 7) or (i > 7 and j < 3)
            if corner:
                if i in (0, 2, 8, 10) or j in (0, 2, 8, 10) or (i in (1, 9) and j in (1, 9)):
                    d.rectangle([x0 + i * c, y0 + j * c, x0 + (i + 1) * c, y0 + (j + 1) * c], fill=OUTL)
            elif rng.random() < 0.45:
                d.rectangle([x0 + i * c, y0 + j * c, x0 + (i + 1) * c, y0 + (j + 1) * c], fill=OUTL)

def note(d, x, y, s=1.0):
    d.rounded_rectangle([x - 90 * s, y - 45 * s, x + 90 * s, y + 45 * s], radius=int(10 * s), fill=(160, 210, 150),
                        outline=OUTL, width=4)
    d.ellipse([x - 26 * s, y - 26 * s, x + 26 * s, y + 26 * s], fill=(120, 180, 110), outline=OUTL, width=3)

def satellite(d, x, y, s=1.0):
    d.rectangle([x - 40 * s, y - 40 * s, x + 40 * s, y + 40 * s], fill=(220, 220, 230), outline=OUTL, width=5)
    for side in (-1, 1):
        x0 = x + side * 50 * s
        x1 = x + side * 190 * s
        d.rectangle([min(x0, x1), y - 30 * s, max(x0, x1), y + 30 * s], fill=(60, 100, 200), outline=OUTL, width=4)
        for k in range(1, 4):
            xx = x0 + (x1 - x0) * k / 4
            d.line([(xx, y - 30 * s), (xx, y + 30 * s)], fill=OUTL, width=3)

# ---------------------------------------------------------------- props
def wake_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "kid", 330, 1080, 440, T, look=(0.6, 0.3))
    def scr(d, x0, y0, x1, y1):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if lt > 1.0: wifi_x(d, cx, cy + 10, 90)
    phone(d, 760, 1040, 0.8, scr)
    if lt > 1.6: lab_at(frame, "NO INTERNET", 760, 1320, RED, 58)
    if lt > 0.3: top_label(frame, "8:00 AM, TODAY", 380, YEL, 84)

def upi_props(frame, d, T, sc):
    lt = T - sc["s"]
    # chai stall counter
    d.rectangle([560, 1060, 1020, 1300], fill=(200, 120, 70), outline=OUTL, width=6)
    mini(frame, "uncle", 790, 900, 340, T, look=(-0.6, 0.2))
    qr(d, 860, 1100, 140)
    mini(frame, "kid", 250, 1100, 380, T, look=(0.6, 0.0))
    if lt < 3.6:
        def scr(d, x0, y0, x1, y1):
            if lt > 1.4:
                lab_at(frame, "FAILED", (x0 + x1) / 2, (y0 + y1) / 2, RED, 40)
        phone(d, 440, 1010, 0.45, scr)
    else:
        q = ease_back(clamp((lt - 3.6) / 0.5))
        note(d, 450, 1010 - 30 * q, 0.9 * q + 0.01)
        lab_at(frame, "CASH IS BACK", 540, 1360, YEL, 62)
    if lt > 0.3: top_label(frame, "~82 CRORE UPI A DAY", 380, YEL, 76)

def gps_props(frame, d, T, sc):
    lt = T - sc["s"]
    satellite(d, 540, 560 + 10 * math.sin(T * 1.5), 0.9)
    # broadcast rings going down
    for k in range(3):
        ph = (lt * 0.6 + k / 3) % 1.0
        r = 60 + 300 * ph
        col = tuple(int(255 - 100 * ph) for _ in range(3))
        d.arc([540 - r, 600 - r * 0.6, 540 + r, 600 + r * 0.6], 30, 150, fill=col, width=6)
    def scr(d, x0, y0, x1, y1):
        d.rectangle([x0, y0, x1, y1], fill=(220, 236, 210))
        d.line([(x0, y1 - 60), (x1, y0 + 80)], fill=(255, 255, 255), width=14)
        d.line([(x0 + 40, y0), (x0 + 90, y1)], fill=(255, 255, 255), width=14)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        r = 22 + 4 * math.sin(T * 5)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 130, 240), outline=WHITE, width=6)
    phone(d, 540, 1100, 0.75, scr)
    if lt > 2.0: lab_at(frame, "GPS STILL WORKS", 540, 1360, GREEN_OK, 64)
    if lt > 0.3: top_label(frame, "ONE-WAY SIGNAL", 380, YEL, 84)

# stylised continents for the cable map
BLOBS = [((80, 560, 380, 900), LAND), ((180, 940, 360, 1300), LAND), ((460, 560, 640, 760), LAND),
         ((470, 790, 640, 1150), LAND), ((650, 560, 1000, 820), LAND), ((760, 830, 840, 960), (250, 160, 70)),
         ((830, 1110, 1010, 1240), LAND)]
CABLES = [[(360, 700), (430, 690), (470, 660)], [(330, 1000), (420, 950), (490, 880)],
          [(620, 980), (700, 920), (780, 900)], [(820, 940), (880, 1000), (910, 1120)],
          [(940, 760), (1060, 700)], [(10, 720), (90, 700)], [(800, 940), (900, 880), (960, 800)]]
def map_props(frame, d, T, sc, grow=True):
    lt = T - sc["s"]
    for b, c in BLOBS:
        d.ellipse(b, fill=c, outline=OUTL, width=5)
    p = ease_out(clamp((lt - 0.8) / 2.2)) if grow else 1.0
    for cab in CABLES:
        n = max(2, int(len(cab) * p + 0.999))
        pts = cab[:n]
        d.line(pts, fill=OUTL, width=14, joint="curve")
        d.line(pts, fill=CABLE, width=7, joint="curve")
    if grow:
        lab_at(frame, "INDIA", 800, 1000, WHITE, 40)
        if lt > 0.3: top_label(frame, "99% UNDER THE SEA" if lt > 3.0 else "UNDER THE SEA", 380, YEL, 84)

def wrap_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "earth", 540, 980, 420, T, state=T * 0.3)
    n = int(clamp((lt - 0.8) / 3.0) * 37)
    for k in range(min(n, 14)):
        rx, ry = 250 + k * 10, 60 + k * 9
        ang = k * 13
        d.arc([540 - rx, 980 - ry, 540 + rx, 980 + ry], 0, 360, fill=CABLE, width=4)
    lab_at(frame, f"x{max(n, 1)}", 540, 1330, YEL, 110)
    if lt > 0.3: top_label(frame, "1.5 MILLION+ KM", 380, YEL, 84)

def hose_props(frame, d, T, sc):
    lt = T - sc["s"]
    # cable cross-section, scaled up
    cx, cy = 540, 960
    p = ease_back(clamp((lt - 0.4) / 0.6))
    R = 260 * p
    if R > 4:
        for r, col in ((R, (40, 40, 46)), (R * 0.82, (220, 220, 220)), (R * 0.6, (200, 160, 90)),
                       (R * 0.42, (240, 240, 240)), (R * 0.2, (255, 220, 120))):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=OUTL, width=4)
        if lt > 2.4:
            for k in range(8):
                a = k / 8 * 2 * math.pi
                x, y = cx + R * 0.11 * math.cos(a), cy + R * 0.11 * math.sin(a)
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(80, 200, 255))
    if lt > 1.2: lab_at(frame, "GARDEN-HOSE THICK", 540, 640, WHITE, 60)
    if lt > 2.6: lab_at(frame, "FIBRES: HAIR-THIN", 540, 1300, YEL, 60)
    if lt > 0.3: top_label(frame, "INSIDE A CABLE", 380, YEL, 84)

def anchor(d, x, y, s=1.0):
    d.line([(x, y - 140 * s), (x, y + 60 * s)], fill=GREY, width=int(16 * s))
    d.ellipse([x - 22 * s, y - 170 * s, x + 22 * s, y - 126 * s], outline=GREY, width=int(10 * s))
    d.line([(x - 50 * s, y - 100 * s), (x + 50 * s, y - 100 * s)], fill=GREY, width=int(12 * s))
    d.arc([x - 90 * s, y - 40 * s, x + 90 * s, y + 80 * s], 20, 160, fill=GREY, width=int(16 * s))

def fault_props(frame, d, T, sc):
    lt = T - sc["s"]
    # cable on the seabed
    snap = lt > 3.0
    if not snap:
        d.line([(0, 1230), (W, 1230)], fill=OUTL, width=18); d.line([(0, 1230), (W, 1230)], fill=CABLE, width=9)
    else:
        d.line([(0, 1230), (500, 1230)], fill=OUTL, width=18); d.line([(0, 1230), (500, 1230)], fill=CABLE, width=9)
        d.line([(580, 1230), (W, 1230)], fill=OUTL, width=18); d.line([(580, 1230), (W, 1230)], fill=CABLE, width=9)
        for k in range(5):
            a = k * 1.3 + T * 8
            d.line([(540, 1230), (540 + 40 * math.cos(a), 1230 + 40 * math.sin(a))], fill=YEL, width=5)
    ax = -100 + 640 * ease_out(clamp((lt - 0.6) / 2.4))
    d.line([(ax, 600), (ax, 1100)], fill=GREY, width=6)
    anchor(d, ax, 1200, 0.9)
    # tiny fish, label myth
    mini(frame, "fish", 860, 820, 150, T)
    if lt > 1.0: lab_at(frame, "~200 BREAKS A YEAR", 540, 580, WHITE, 60)
    if lt > 4.2: lab_at(frame, "SHARKS? RARELY", 540, 1360, YEL, 62)
    if lt > 0.3: top_label(frame, "ANCHORS + NETS", 380, YEL, 84)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # 1969 computer terminal
    d.rectangle([220, 640, 860, 1160], fill=(214, 206, 180), outline=OUTL, width=6)
    d.rectangle([270, 690, 810, 1040], fill=(20, 30, 24), outline=OUTL, width=5)
    d.rectangle([300, 1180, 780, 1260], fill=(190, 180, 150), outline=OUTL, width=5)
    typed = "LOGIN"
    n = int(clamp((lt - 0.6) / 1.4) * 2.999) if lt < 3.0 else 2
    txt = typed[:n]
    if txt:
        l = label(txt, 150, (90, 255, 120)); comp(frame, l, 310, 700)
    if lt > 2.8:
        q = ease_back(clamp((lt - 2.8) / 0.4))
        lab_at(frame, "CRASH!", 540, 970, RED, int(96 * q) + 2)
    if lt > 3.8: lab_at(frame, "29 OCT 1969", 540, 1340, YEL, 66)
    if lt > 0.3: top_label(frame, "THE FIRST MESSAGE", 380, YEL, 84)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wake", s=4.0, e=11.0, bg_fn=room_bg, clock="DAY 1", props=wake_props,
         narr="You wake up. NO reels, NO chats, NO video calls. The whole internet is GONE.", n_at=4.2,
         narr_y=1590),
    dict(id="upi", s=11.0, e=18.0, bg_fn=street_bg, clock="CHAI TIME", props=upi_props,
         narr="UPI handles about 82 CRORE payments a day. Today, the QR code is just a sticker.",
         n_at=11.2, narr_y=1590),
    dict(id="gps", s=18.0, e=25.0, bg_fn=space_bg, clock="SURPRISE", props=gps_props,
         narr="But GPS still WORKS! Satellites only broadcast, and your phone just LISTENS.", n_at=18.2,
         narr_y=1590),
    dict(id="map", s=25.0, e=32.0, bg_fn=sea_bg, clock="WHERE IS IT?", props=map_props,
         narr="Where does the internet live? SEAFLOOR cables carry over 99% of data between continents.",
         n_at=25.2, narr_y=1600),
    dict(id="wrap", s=32.0, e=39.0, bg_fn=space_bg, clock="SO MUCH CABLE", props=wrap_props,
         narr="600+ cables, over 1.5 MILLION KM long. That wraps Earth about 37 TIMES.", n_at=32.2,
         narr_y=1590),
    dict(id="hose", s=39.0, e=46.0, bg_fn=sea_bg, clock="ZOOM IN", props=hose_props,
         narr="Most of it is only as thick as a GARDEN HOSE, with glass fibres thin as a HAIR.", n_at=39.2,
         narr_y=1590),
    dict(id="fault", s=46.0, e=TW, bg_fn=seabed_bg, clock="BREAKDOWNS", props=fault_props,
         narr="About 200 faults a year, mostly fishing gear and ship ANCHORS. Shark bites? Super rare.",
         n_at=46.2, narr_y=1590),
    dict(id="twist", s=TW, e=60.0, bg_fn=lab_bg, clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: the internet's FIRST message was meant to be LOGIN. It CRASHED after just LO.",
         n_at=TW + 0.2, narr_y=1590),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.1)
        if p > 0.05:
            wifi_x(d, 540, 1420, 160 * p, col=WHITE)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 470, 0.2, "pop"),
        (title([("THE INTERNET", WHITE)], 140), 680, 0.75, "right"),
        (title([("VANISHED FOR A DAY?", YEL)], 104), 830, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 100), 470, 0.15),
                      (title([("do first?", WHITE)], 104), 600, 0.45)],
               row=[("kid", 1), ("earth", 1), ("uncle", "hat"), ("fish", 1), ("chai", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, minor=True),
           dict(t0=18.0, t1=46.0, melody=True), dict(t0=46.0, t1=TW - 0.15, minor=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=46.0, dur=7.0, g=0.10)],
    fx=[("powerdown", 4.6, 0.3), ("click", 12.6, 0.3), ("ding", 15.0, 0.15), ("tick", 19.0, 0.2),
        ("ding", 20.4, 0.2), ("underwater", 25.3, 0.15, dict(dd=6.0)), ("whoosh", 33.0, 0.2),
        ("pop", 40.0, 0.3), ("underwater", 46.3, 0.15, dict(dd=6.0)), ("crash", 49.0, 0.3),
        ("click", TW + 1.0, 0.3), ("click", TW + 1.6, 0.3), ("powerdown", TW + 2.8, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_the_internet_vanished_for_a_day")
